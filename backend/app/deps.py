from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from .database import AsyncSessionLocal
from .core.config import settings
from .models import APIKey, User

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
    except (JWTError, ValueError, TypeError):
        return None
    # selectinload(User.role): role.name is read synchronously downstream
    # (require_role/require_any_role, UserRead serialization) — async
    # SQLAlchemy can't lazy-load a relationship outside an `await`, so it must
    # already be loaded by the time this function returns.
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


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


async def _get_api_key(
    x_api_key: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> Optional[APIKey]:
    if not x_api_key:
        return None
    result = await db.execute(
        select(APIKey).options(selectinload(APIKey.user)).where(APIKey.key == x_api_key)
    )
    key = result.scalar_one_or_none()
    if not key or not key.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key")
    if key.quota_limit is not None and key.quota_used >= key.quota_limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="API key quota exceeded")
    return key


async def get_current_user_or_api_key(
    api_key: Optional[APIKey] = Depends(_get_api_key),
    token: Optional[str] = Depends(get_token_from_request),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Auth dependency for developer-facing endpoints: accepts an X-API-Key
    header (metered against that key's quota), the browser's httpOnly cookie,
    or a JWT bearer token.
    """
    if api_key is not None:
        api_key.quota_used += 1
        db.add(api_key)
        await db.commit()
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
