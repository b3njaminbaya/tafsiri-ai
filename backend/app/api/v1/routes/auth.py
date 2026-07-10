from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .... import schemas
from ....core.config import settings
from ....core.limiter import limiter
from ....deps import ACCESS_TOKEN_COOKIE_NAME, get_current_active_user, get_db, require_role
from ....email_client import EmailClient, get_email_client
from ....models import APIKey, AuthToken, Role, User
from ....oauth_client import OAuthClient, OAuthError, get_github_oauth_client, get_google_oauth_client
from ....security import create_access_token, get_password_hash, normalize_email, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# Default roles (admin/translator/user) are seeded by the initial Alembic
# migration (20260710_0001_initial_schema) — not created at request time.

RESET_TOKEN_TTL = timedelta(hours=1)
VERIFY_TOKEN_TTL = timedelta(hours=24)


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.access_token_cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


async def _issue_token(db: AsyncSession, user_id: int, purpose: str, ttl: timedelta) -> str:
    raw = token_urlsafe(32)
    db.add(
        AuthToken(
            user_id=user_id,
            token=raw,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + ttl,
        )
    )
    await db.commit()
    return raw


async def _consume_token(db: AsyncSession, token: str, purpose: str) -> Optional[User]:
    result = await db.execute(
        select(AuthToken).where(AuthToken.token == token, AuthToken.purpose == purpose)
    )
    record = result.scalar_one_or_none()
    if not record or record.used_at is not None:
        return None
    # SQLite (aiosqlite) doesn't round-trip tzinfo the way Postgres/asyncpg
    # does for a DateTime(timezone=True) column — it comes back naive even
    # though it was stored as UTC-aware. Tag it before comparing rather than
    # letting the two DB backends disagree on whether this comparison is
    # even legal (naive vs. aware datetimes can't be compared directly).
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        return None
    record.used_at = datetime.now(timezone.utc)
    await db.commit()
    return user


@router.post("/register", response_model=schemas.UserRead, summary="Register with email/password")
@limiter.limit("10/minute")
async def register(
    request: Request,
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    email_client: EmailClient = Depends(get_email_client),
):
    email = normalize_email(user_in.email)
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # First-admin bootstrap: there's no other way to create an admin account
    # without a direct database edit, so an operator-configured email
    # (FIRST_ADMIN_EMAIL) is promoted automatically at registration time.
    # Unset by default (""), in which case this never matches and every
    # registration behaves exactly as before.
    role_name = (
        "admin"
        if settings.first_admin_email and email == normalize_email(settings.first_admin_email)
        else "user"
    )
    role = (await db.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()

    user = User(
        email=email,
        hashed_password=get_password_hash(user_in.password),
        role=role,
    )
    db.add(user)
    await db.commit()

    verify_token = await _issue_token(db, user.id, "email_verification", VERIFY_TOKEN_TTL)
    verify_link = f"{settings.frontend_base_url}/verify-email?token={verify_token}"
    email_client.send(
        user.email,
        "Verify your NMT Agent account",
        f"Welcome! Verify your email by visiting:\n\n{verify_link}\n\nThis link expires in 24 hours.",
    )

    return user


@router.post("/login", response_model=schemas.Token, summary="Obtain JWT access token")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == normalize_email(form_data.username)))
    user = result.scalar_one_or_none()
    # OAuth-only accounts have no password (hashed_password is NULL) — treat
    # exactly like a wrong password rather than erroring on the None.
    if (
        not user
        or not user.hashed_password
        or not verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(subject=str(user.id))
    _set_auth_cookie(response, token)
    return schemas.Token(access_token=token)


@router.post("/logout", summary="Clear the browser auth cookie")
async def logout(response: Response):
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME, path="/")
    return {"message": "Logged out"}


@router.get("/me", response_model=schemas.UserRead, summary="Get current user")
async def me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=schemas.UserRead, summary="Update your profile (display name)")
async def update_me(
    body: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if body.display_name is not None:
        current_user.display_name = body.display_name.strip() or None
    db.add(current_user)
    await db.commit()
    return current_user


OAUTH_STATE_COOKIE_NAME = "oauth_state"


async def _find_or_create_oauth_user(
    db: AsyncSession, provider: str, subject: str, email: str
) -> User:
    email = normalize_email(email)
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.oauth_provider == provider, User.oauth_subject == subject)
    )
    user = result.scalar_one_or_none()
    if user:
        return user

    # An existing password-based account with the same email gets the OAuth
    # identity linked to it, rather than creating a second, disconnected
    # account for the same person.
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    if user:
        user.oauth_provider = provider
        user.oauth_subject = subject
        await db.commit()
        return user

    role_name = (
        "admin"
        if settings.first_admin_email and email == normalize_email(settings.first_admin_email)
        else "user"
    )
    role = (await db.execute(select(Role).where(Role.name == role_name))).scalar_one_or_none()
    user = User(
        email=email,
        hashed_password=None,
        is_verified=True,  # the provider already verified this email address
        oauth_provider=provider,
        oauth_subject=subject,
        role=role,
    )
    db.add(user)
    await db.commit()
    return user


@router.get(
    "/oauth/providers",
    summary="Which OAuth providers are configured — the frontend uses this to "
    "show/hide/disable login buttons rather than offering a button that 503s.",
)
def oauth_providers(
    google_client: OAuthClient = Depends(get_google_oauth_client),
    github_client: OAuthClient = Depends(get_github_oauth_client),
):
    return {"google": google_client.is_configured, "github": github_client.is_configured}


def _oauth_login(client: OAuthClient) -> RedirectResponse:
    if not client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{client.config.name} OAuth is not configured",
        )
    state = token_urlsafe(16)
    redirect = RedirectResponse(client.get_authorize_url(state))
    redirect.set_cookie(
        OAUTH_STATE_COOKIE_NAME,
        state,
        httponly=True,
        samesite="lax",
        secure=settings.access_token_cookie_secure,
        max_age=600,
        path="/api/v1/auth/oauth",
    )
    return redirect


async def _oauth_callback(
    client: OAuthClient, code: str, state: str, request: Request, db: AsyncSession
) -> RedirectResponse:
    if not client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{client.config.name} OAuth is not configured",
        )
    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE_NAME)
    if not cookie_state or cookie_state != state:
        return RedirectResponse(f"{settings.frontend_base_url}/login?oauth_error=invalid_state")

    try:
        access_token = client.exchange_code(code)
        email, subject = client.get_user_email_and_subject(access_token)
        user = await _find_or_create_oauth_user(db, client.config.name, subject, email)
    except OAuthError:
        return RedirectResponse(f"{settings.frontend_base_url}/login?oauth_error=failed")

    jwt_token = create_access_token(subject=str(user.id))
    redirect = RedirectResponse(f"{settings.frontend_base_url}/translate")
    redirect.delete_cookie(OAUTH_STATE_COOKIE_NAME, path="/api/v1/auth/oauth")
    _set_auth_cookie(redirect, jwt_token)
    return redirect


@router.get("/oauth/google/login", summary="Redirect to Google for OAuth login")
def google_login(google_client: OAuthClient = Depends(get_google_oauth_client)):
    return _oauth_login(google_client)


@router.get("/oauth/google/callback", summary="Google OAuth callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    google_client: OAuthClient = Depends(get_google_oauth_client),
):
    return await _oauth_callback(google_client, code, state, request, db)


@router.get("/oauth/github/login", summary="Redirect to GitHub for OAuth login")
def github_login(github_client: OAuthClient = Depends(get_github_oauth_client)):
    return _oauth_login(github_client)


@router.get("/oauth/github/callback", summary="GitHub OAuth callback")
async def github_callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    github_client: OAuthClient = Depends(get_github_oauth_client),
):
    return await _oauth_callback(github_client, code, state, request, db)


@router.post("/forgot-password", summary="Request a password reset email")
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    body: schemas.ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    email_client: EmailClient = Depends(get_email_client),
):
    result = await db.execute(select(User).where(User.email == normalize_email(body.email)))
    user = result.scalar_one_or_none()
    # Same response regardless of whether the email exists — otherwise this
    # endpoint becomes a user-enumeration oracle.
    if user:
        reset_token = await _issue_token(db, user.id, "password_reset", RESET_TOKEN_TTL)
        reset_link = f"{settings.frontend_base_url}/reset-password?token={reset_token}"
        email_client.send(
            user.email,
            "Reset your NMT Agent password",
            f"Reset your password by visiting:\n\n{reset_link}\n\n"
            "This link expires in 1 hour. If you didn't request this, ignore this email.",
        )
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password", summary="Reset password using a token from the forgot-password email")
async def reset_password(body: schemas.ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await _consume_token(db, body.token, "password_reset")
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.hashed_password = get_password_hash(body.new_password)
    await db.commit()
    return {"message": "Password updated"}


@router.post("/verify-email", summary="Verify email using a token from the verification email")
async def verify_email(body: schemas.VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    user = await _consume_token(db, body.token, "email_verification")
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.is_verified = True
    await db.commit()
    return {"message": "Email verified"}


@router.post("/resend-verification", summary="Resend the email verification link")
@limiter.limit("5/minute")
async def resend_verification(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    email_client: EmailClient = Depends(get_email_client),
):
    if current_user.is_verified:
        return {"message": "Already verified"}
    verify_token = await _issue_token(db, current_user.id, "email_verification", VERIFY_TOKEN_TTL)
    verify_link = f"{settings.frontend_base_url}/verify-email?token={verify_token}"
    email_client.send(
        current_user.email,
        "Verify your NMT Agent account",
        f"Verify your email by visiting:\n\n{verify_link}\n\nThis link expires in 24 hours.",
    )
    return {"message": "Verification email sent"}


@router.post("/api-keys", response_model=schemas.APIKeyCreateResponse, summary="Create an API key")
async def create_api_key(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    key_value = token_urlsafe(32)
    api_key = APIKey(key=key_value, user_id=current_user.id, is_active=True)
    db.add(api_key)
    await db.commit()
    return schemas.APIKeyCreateResponse(api_key=api_key)


@router.get("/api-keys", response_model=list[schemas.APIKeyRead], summary="List my API keys")
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(APIKey).where(APIKey.user_id == current_user.id))
    return result.scalars().all()


@router.post("/api-keys/{key_id}/revoke", summary="Revoke an API key")
async def revoke_api_key(
    key_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == current_user.id)
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    key.is_active = False
    await db.commit()
    return {"message": "API key revoked"}


@router.post("/promote/{user_id}", summary="Promote a user to translator", dependencies=[Depends(require_role("admin"))])
async def promote_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    translator_role = (
        await db.execute(select(Role).where(Role.name == "translator"))
    ).scalar_one_or_none()
    user.role = translator_role
    await db.commit()
    return {"message": "User promoted"}
