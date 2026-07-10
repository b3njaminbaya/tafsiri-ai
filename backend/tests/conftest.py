import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SECRET_KEY", "test-secret")

from app.database import Base
from app.deps import get_db
from app.ml_client import get_ml_client
from app.models import Role, User
from app.main import app
from app.core.limiter import limiter
from app.storage import get_s3_client, get_s3_public_client


class FakeMLClient:
    """In-process stand-in for ml-service, so tests exercise the real
    persistence/history/feedback logic without needing a model loaded or a
    network call to a running ml-service.
    """

    def translate(self, text: str, target_lang: str, source_lang=None, domain=None) -> dict:
        return {
            "translation": f"[{target_lang}] {text[::-1]}",
            "source_lang": source_lang or "en",
            "confidence": 0.87,
        }


class FakeS3Client:
    """In-memory stand-in for boto3's S3 client — same rationale as
    FakeMLClient: exercises the real upload/list/download logic without a
    running MinIO instance.
    """

    def __init__(self):
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, Bucket: str, Key: str, Body: bytes) -> None:
        self.objects[(Bucket, Key)] = Body

    def generate_presigned_url(self, operation: str, Params: dict, ExpiresIn: int) -> str:
        bucket, key = Params["Bucket"], Params["Key"]
        return f"http://fake-s3.local/{bucket}/{key}?expires={ExpiresIn}"


_fake_s3 = FakeS3Client()

app.dependency_overrides[get_ml_client] = lambda: FakeMLClient()
app.dependency_overrides[get_s3_client] = lambda: _fake_s3
app.dependency_overrides[get_s3_public_client] = lambda: _fake_s3

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session", autouse=True)
def seed_roles():
    db = TestingSessionLocal()
    for name in ["admin", "translator", "user"]:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name))
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def _reset_rate_limits():
    # The limiter is a module-level singleton shared across the whole test
    # session (same as in a real running app) — without this, tests that
    # register/login several times would start tripping the real 5/min and
    # 10/min limits depending on test order, since TestClient requests all
    # share the same fake remote address.
    limiter.reset()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def promote_actor_to_admin(client):
    """Promote a freshly-registered user straight to 'admin' via direct DB access.

    There is currently no API path to create the first admin account (a real
    gap — see docs/AUDIT.md) so tests that need an admin actor reach into the
    test database directly rather than exercising a bootstrap endpoint that
    doesn't exist yet.
    """

    def _promote(email: str, password: str = "secret123") -> str:
        from .helpers import register_and_login

        token = register_and_login(client, email, password)
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            user.role = db.query(Role).filter(Role.name == "admin").first()
            db.commit()
        finally:
            db.close()
        return token

    return _promote
