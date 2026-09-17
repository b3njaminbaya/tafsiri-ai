from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from .database import AsyncSessionLocal
from .core.config import settings
from .models import APIKey, User
from .security import hash_api_key

ACCESS_TOKEN_COOKIE_NAME = "access_token"

# auto_error=False: some routes (translate) accept either a bearer token or an
# X-API-Key header, so a missing bearer token must not short-circuit before the
# API-key path gets a chance to run.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


async def get_token_from_request(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[str]:
    """The browser SPA authenticates via an httpOnly cookie (not readable by
    JS, so not stealable via XSS the way a localStorage token was); API/CLI
    consumers keep using a Bearer header exactly as before. An explicit
    Bearer header wins if both are present: it's a deliberate statement of
    which identity to use, where a cookie is just ambient browser state
    automatically attached to every same-site request — an API client (or a
    test) explicitly asserting "act as this token" should never be silently
    overridden by whatever happens to be sitting in the cookie jar.
    """
    return bearer_token or request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)


async def _user_from_token(token: str, db: AsyncSession) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub"))
        token_version = int(payload.get("tv", 0))
    except (JWTError, ValueError, TypeError):
        return None
    # selectinload(User.role): role.name is read synchronously downstream
    # (require_role/require_any_role, UserRead serialization) — async
    # SQLAlchemy can't lazy-load a relationship outside an `await`, so it must
    # already be loaded by the time this function returns.
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None
    # A password reset bumps User.token_version (see auth.py:reset_password);
    # a token minted before that reset carries the old version and must stop
    # working immediately, not linger for the rest of its 7-day life.
    if user.token_version != token_version:
        return None
    return user


async def get_current_user(
    token: Optional[str] = Depends(get_token_from_request), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    user = await _user_from_token(token, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role_name: str):
    async def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role or current_user.role.name != role_name:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _checker


def require_any_role(*role_names: str):
    async def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role or current_user.role.name not in role_names:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _checker


async def get_api_key(
    x_api_key: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Optional[APIKey]:
    """Resolves (but does not charge) the X-API-Key header. Quota is charged
    separately and atomically by consume_api_key_quota, right before the
    metered work actually happens — see translate.py. This function only
    rejects keys that are missing/invalid/inactive/already-exhausted; the
    exhaustion check here is advisory (a fast-fail for the common case), the
    real, race-safe enforcement is the conditional UPDATE in
    consume_api_key_quota.
    """
    if not x_api_key:
        return None
    result = await db.execute(
        select(APIKey)
        .options(selectinload(APIKey.user).selectinload(User.role))
        .where(APIKey.hashed_key == hash_api_key(x_api_key))
    )
    key = result.scalar_one_or_none()
    if not key or not key.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key")
    if key.quota_limit is not None and key.quota_used >= key.quota_limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="API key quota exceeded")
    return key


async def consume_api_key_quota(api_key: Optional[APIKey], db: AsyncSession, amount: int = 1) -> bool:
    """Atomically reserves `amount` units of quota via a single conditional
    UPDATE (not a separate check-then-write), so concurrent requests near the
    limit can't all pass the check before any of them commits — the race
    condition the old check-in-get_api_key/increment-in-the-caller split had.
    Call this right before doing the metered work (the ml-service call), not
    at auth time, so a cache hit (no ml-service call at all) never charges
    quota; on a downstream failure, pair it with refund_api_key_quota.
    No-op (returns True) for JWT/cookie sessions (api_key is None) — those
    aren't quota-metered, only rate-limited.
    """
    if api_key is None:
        return True
    result = await db.execute(
        update(APIKey)
        .where(
            APIKey.id == api_key.id,
            (APIKey.quota_limit.is_(None)) | (APIKey.quota_used + amount <= APIKey.quota_limit),
        )
        .values(quota_used=APIKey.quota_used + amount)
    )
    await db.commit()
    return result.rowcount > 0


async def refund_api_key_quota(api_key: Optional[APIKey], db: AsyncSession, amount: int = 1) -> None:
    """Undoes a consume_api_key_quota reservation after the metered work it
    was reserved for turned out to fail (e.g. ml-service was unreachable) —
    a failed request shouldn't permanently cost the caller quota it never
    got a translation for.
    """
    if api_key is None:
        return
    await db.execute(
        update(APIKey).where(APIKey.id == api_key.id).values(quota_used=APIKey.quota_used - amount)
    )
    await db.commit()


async def get_current_user_or_api_key(
    api_key: Optional[APIKey] = Depends(get_api_key),
    token: Optional[str] = Depends(get_token_from_request),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Auth dependency for developer-facing endpoints: accepts an X-API-Key
    header, the browser's httpOnly cookie, or a JWT bearer token. Callers
    that need to meter usage should also depend on get_api_key directly
    (FastAPI caches it per-request, so it isn't re-resolved) and call
    consume_api_key_quota/refund_api_key_quota themselves around the actual
    metered work.
    """
    if api_key is not None:
        return api_key.user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    user = await _user_from_token(token, db)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
