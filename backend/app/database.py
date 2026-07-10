from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from .core.config import settings


def to_async_url(url: str) -> str:
    """DATABASE_URL stays in its existing sync-driver form (postgresql+psycopg2://)
    since Alembic migrations run against it unchanged; the app's runtime engine
    below needs the async driver instead, so this converts just for that.
    """
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://") and "aiosqlite" not in url:
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url


engine = create_async_engine(to_async_url(settings.database_url), pool_pre_ping=True)
# expire_on_commit=False: async SQLAlchemy can't implicitly re-fetch expired
# attributes outside an `await` (accessing one raises MissingGreenlet), so
# attributes read after a commit (e.g. a freshly-inserted row's id) need to
# stay populated from the values already in memory rather than being expired
# and silently re-queried.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)
Base = declarative_base()
