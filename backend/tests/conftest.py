import asyncio
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("SECRET_KEY", "test-secret")

from app.database import Base
from app.deps import get_db
from app.billing_client import BillingError, get_stripe_client
from app.cache import get_cache_client
from app.oauth_client import get_github_oauth_client, get_google_oauth_client
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

    def __init__(self):
        self.call_count = 0

    async def translate(self, text: str, target_lang: str, source_lang=None, domain=None, forced_terms=None) -> dict:
        self.call_count += 1
        return {
            "translation": f"[{target_lang}] {text[::-1]}",
            "source_lang": source_lang or "en",
            "confidence": 0.87,
            "applied_glossary_terms": forced_terms or [],
        }

    async def translate_batch(self, items: list) -> list:
        return [
            await self.translate(
                item["text"],
                item["target_lang"],
                item.get("source_lang"),
                item.get("domain"),
                item.get("forced_terms"),
            )
            for item in items
        ]

    async def get_languages(self) -> dict:
        return {"languages": [{"code": "en", "name": "English"}, {"code": "es", "name": "Spanish"}]}

    async def get_health(self) -> dict:
        return {"status": "ok", "model_name": "fake-model", "model_loaded": True}


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


class FakeCacheClient:
    """In-memory stand-in for the Redis-backed CacheClient — same rationale
    as FakeMLClient/FakeS3Client: exercises the real cache-hit/miss logic in
    the translate route without a running Redis instance.
    """

    def __init__(self):
        self.store: dict = {}

    @staticmethod
    def translation_key(text, source_lang, target_lang, domain) -> str:
        return f"{source_lang or 'auto'}|{target_lang}|{domain or ''}|{text}"

    def get(self, key: str):
        return self.store.get(key)

    def set(self, key: str, value: dict) -> None:
        self.store[key] = value


class FakeStripeClient:
    """In-process stand-in for the Stripe SDK — same rationale as the other
    fakes. There are no Stripe test-mode credentials in this environment, so
    this is what the billing routes are actually verified against; see
    app/billing_client.py's docstring for what that does and doesn't prove.
    """

    def __init__(self):
        self.created_sessions: list = []
        self.configured = True
        self.webhook_configured = True

    @property
    def is_configured(self) -> bool:
        return self.configured

    @property
    def webhook_is_configured(self) -> bool:
        return self.webhook_configured

    def create_checkout_session(self, price_id, customer_email, success_url, cancel_url) -> str:
        self.created_sessions.append({"price_id": price_id, "customer_email": customer_email})
        return f"https://fake-stripe.local/checkout/{price_id}"

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> dict:
        import json

        if sig_header != "valid-test-signature":
            raise BillingError("invalid signature")
        return json.loads(payload)


class _FakeOAuthConfig:
    def __init__(self, name: str):
        self.name = name


class FakeOAuthClient:
    """In-process stand-in for Google/GitHub's OAuth HTTP APIs — same
    rationale as the other fakes. There's no way to exercise a real OAuth
    consent screen from an automated test, so this is what the OAuth routes
    are actually verified against; the login/callback flow logic (state
    validation, account linking, cookie issuance) is real and real-tested,
    only the provider HTTP calls are faked.
    """

    def __init__(self, name: str, configured: bool = True):
        self.config = _FakeOAuthConfig(name)
        self.configured = configured
        self.next_email = f"{name}user@example.com"
        self.next_subject = "fake-subject-1"
        self.fail_exchange = False

    @property
    def is_configured(self) -> bool:
        return self.configured

    def get_authorize_url(self, state: str) -> str:
        return f"https://fake-{self.config.name}.local/authorize?state={state}"

    def exchange_code(self, code: str) -> str:
        if self.fail_exchange or code == "bad-code":
            from app.oauth_client import OAuthError

            raise OAuthError("code exchange failed")
        return "fake-access-token"

    def get_user_email_and_subject(self, access_token: str):
        return self.next_email, self.next_subject


_fake_ml = FakeMLClient()
_fake_s3 = FakeS3Client()
_fake_cache = FakeCacheClient()
_fake_stripe = FakeStripeClient()
_fake_google_oauth = FakeOAuthClient("google")
_fake_github_oauth = FakeOAuthClient("github")

app.dependency_overrides[get_ml_client] = lambda: _fake_ml
app.dependency_overrides[get_s3_client] = lambda: _fake_s3
app.dependency_overrides[get_s3_public_client] = lambda: _fake_s3
app.dependency_overrides[get_cache_client] = lambda: _fake_cache
app.dependency_overrides[get_stripe_client] = lambda: _fake_stripe
app.dependency_overrides[get_google_oauth_client] = lambda: _fake_google_oauth
app.dependency_overrides[get_github_oauth_client] = lambda: _fake_github_oauth

engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def run_db(fn):
    """Bridges a synchronous test function into the async test DB.

    Test functions themselves stay plain `def` (TestClient runs the app's
    async routes fine without pytest-asyncio); this is only for the handful
    of test helpers that need to poke the DB directly, bypassing the API —
    each gets its own short-lived event loop via asyncio.run(), which is safe
    for aiosqlite (it doesn't hard-bind a connection to one loop the way an
    asyncpg pool would).
    """

    async def _impl():
        async with TestingSessionLocal() as db:
            return await fn(db)

    return asyncio.run(_impl())


async def _create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(_create_all())


async def _override_get_db():
    async with TestingSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session", autouse=True)
def seed_roles():
    async def _seed(db):
        for name in ["admin", "translator", "user"]:
            existing = (await db.execute(select(Role).where(Role.name == name))).scalar_one_or_none()
            if not existing:
                db.add(Role(name=name))
        await db.commit()

    run_db(_seed)


@pytest.fixture(autouse=True)
def _reset_test_state():
    # The limiter, fake ML client, and fake cache are all module-level
    # singletons shared across the whole test session (same as their real
    # counterparts in a running app) — without resetting them, tests would
    # leak rate-limit counts, cached translations, and call counts into each
    # other depending on test order.
    limiter.reset()
    _fake_ml.call_count = 0
    _fake_cache.store.clear()
    _fake_stripe.created_sessions.clear()
    _fake_stripe.configured = True
    _fake_stripe.webhook_configured = True
    for oauth_fake, name in ((_fake_google_oauth, "google"), (_fake_github_oauth, "github")):
        oauth_fake.configured = True
        oauth_fake.fail_exchange = False
        oauth_fake.next_email = f"{name}user@example.com"
        oauth_fake.next_subject = "fake-subject-1"
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

        async def _do_promote(db):
            user = (await db.execute(select(User).where(User.email == email))).scalar_one()
            admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
            user.role = admin_role
            await db.commit()

        run_db(_do_promote)
        return token

    return _promote
