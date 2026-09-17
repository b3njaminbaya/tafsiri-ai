from urllib.parse import parse_qs, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from .core.config import settings


def to_async_url(url: str) -> str:
    """DATABASE_URL stays in its existing sync-driver form (postgresql+psycopg2://)
    since Alembic migrations run against it unchanged; the app's runtime engine
    below needs the async driver instead, so this converts just for that.

    Also strips the query string entirely. psycopg2 (the sync driver) is
    built on real libpq, which understands every libpq connection parameter
    a provider might put in the URL — including newer ones like
    channel_binding, which Neon's connection strings include by default.
    asyncpg implements its own wire protocol, not libpq, and does not
    recognize channel_binding at all: passing it through raises
    `TypeError: connect() got an unexpected keyword argument 'channel_binding'`
    — verified directly against a real Neon database, not assumed. TLS
    intent (sslmode=require/verify-ca/verify-full) is preserved separately
    via `requires_ssl()`/`connect_args`, below, since asyncpg wants that
    expressed as a connect() argument, not a URL query parameter.
    """
    if url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://") and "aiosqlite" not in url:
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    else:
        return url

    parts = urlsplit(url)
    return urlunsplit(parts._replace(query=""))


def requires_ssl(url: str) -> bool:
    sslmode = parse_qs(urlsplit(url).query).get("sslmode", [""])[0]
    return sslmode in ("require", "verify-ca", "verify-full")


_connect_args = {"ssl": True} if requires_ssl(settings.database_url) else {}
engine = create_async_engine(
    to_async_url(settings.database_url), pool_pre_ping=True, connect_args=_connect_args
)
# expire_on_commit=False: async SQLAlchemy can't implicitly re-fetch expired
# attributes outside an `await` (accessing one raises MissingGreenlet), so
# attributes read after a commit (e.g. a freshly-inserted row's id) need to
# stay populated from the values already in memory rather than being expired
# and silently re-queried.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)
Base = declarative_base()
