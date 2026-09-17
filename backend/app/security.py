import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from .core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize_email(email: str) -> str:
    """Emails are conventionally case-insensitive — without this, 'User@x.com'
    and 'user@x.com' register as two different accounts, and a login attempt
    that doesn't exactly match the stored casing (e.g. a browser
    autocapitalizing the first letter) fails as an indistinguishable-from-
    wrong-password 401. Every place an email is stored or looked up should
    go through this first.
    """
    return email.strip().lower()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: str, token_version: int = 0, expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    # "tv" is checked against the user's current User.token_version at
    # validation time (deps._user_from_token) — bumping it (on password
    # reset) invalidates every token issued before that point, without
    # needing a denylist of individual tokens.
    to_encode = {"exp": expire, "sub": str(subject), "tv": token_version}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def hash_api_key(raw_key: str) -> str:
    """Deterministic (unsalted) hash used to look an API key up by exact
    value. Safe without a per-key salt because the input is always a
    high-entropy random token the user never chose (see APIKey.hashed_key),
    unlike a human-chosen password.
    """
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
