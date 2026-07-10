from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from .database import SessionLocal
from .core.config import settings
from .models import APIKey, User

# auto_error=False: some routes (translate) accept either a bearer token or an
# X-API-Key header, so a missing bearer token must not short-circuit before the
# API-key path gets a chance to run.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _user_from_token(token: str, db: Session) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == user_id).first()


def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    user = _user_from_token(token, db)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role_name: str):
    def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.role or current_user.role.name != role_name:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _checker


def _get_api_key(
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[APIKey]:
    if not x_api_key:
        return None
    key = db.query(APIKey).filter(APIKey.key == x_api_key).first()
    if not key or not key.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key")
    if key.quota_limit is not None and key.quota_used >= key.quota_limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="API key quota exceeded")
    return key


def get_current_user_or_api_key(
    api_key: Optional[APIKey] = Depends(_get_api_key),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Auth dependency for developer-facing endpoints: accepts either an
    X-API-Key header (metered against that key's quota) or a JWT bearer token.
    """
    if api_key is not None:
        api_key.quota_used += 1
        db.add(api_key)
        db.commit()
        return api_key.user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    user = _user_from_token(token, db)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
