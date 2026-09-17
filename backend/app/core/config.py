from typing import List
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Tafsiri AI API"
    environment: str = "development"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/nmt",
    )

    # Cookie the browser SPA authenticates with (replaces storing the JWT in
    # localStorage, which was readable — and stealable — by any XSS). API/CLI
    # consumers keep using a plain Bearer header; nothing changes for them.
    access_token_cookie_secure: bool = os.getenv("ENVIRONMENT", "development") != "development"

    # If set, this email is promoted to admin automatically at registration
    # time (case-insensitive) — the only way to get a first admin account
    # otherwise is a direct database edit. Safe to leave unset: nothing
    # happens differently for any other email.
    first_admin_email: str = os.getenv("FIRST_ADMIN_EMAIL", "")

    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:8080")
    backend_base_url: str = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

    # OAuth (Google/GitHub). Both unset by default: the corresponding login
    # button is reported as unavailable (see GET /auth/oauth/providers) and
    # the login/callback endpoints return a clear 503 rather than attempting
    # a call with empty credentials.
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    github_client_id: str = os.getenv("GITHUB_CLIENT_ID", "")
    github_client_secret: str = os.getenv("GITHUB_CLIENT_SECRET", "")

    # Email (password reset, verification, GDPR export links). If SMTP isn't
    # configured, the app doesn't fail — it logs the message it would have
    # sent instead, which is enough to develop and test these flows without
    # a real mail server. See app/email_client.py.
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_address: str = os.getenv("SMTP_FROM_ADDRESS", "noreply@tafsiri.ai")

    ml_service_url: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ml_service_timeout_seconds: float = float(os.getenv("ML_SERVICE_TIMEOUT_SECONDS", "30"))

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # Internal endpoint (container-network hostname, e.g. http://minio:9000) used
    # by the backend itself to put/get objects. Kept separate from
    # minio_public_url because a presigned URL generated against the internal
    # hostname would be unreachable from a browser.
    minio_endpoint_url: str = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")
    # Public-facing endpoint used only when generating presigned download URLs
    # meant to be opened directly in a browser.
    minio_public_url: str = os.getenv("MINIO_PUBLIC_URL", "http://localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket_datasets: str = os.getenv("MINIO_BUCKET_DATASETS", "datasets")
    max_dataset_upload_bytes: int = int(os.getenv("MAX_DATASET_UPLOAD_BYTES", str(50 * 1024 * 1024)))

    # Kept as a plain comma-separated string rather than List[str]: pydantic-
    # settings tries to JSON-decode env values for List-typed fields, which
    # raises on a plain comma-separated string like "http://a,http://b" — the
    # format docker-compose and every example in this repo actually use for
    # CORS_ORIGINS. No wildcard fallback either: CORS runs with
    # allow_credentials=True, and browsers reject "*" combined with
    # credentials anyway, so an explicit dev default is safer than a setting
    # that would silently do nothing.
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Billing (Stripe). Unverified against the real Stripe API in this repo's
    # own development/CI environment — no test-mode credentials are available
    # here. Tested against a fake client (see tests/test_billing.py); wiring
    # real STRIPE_SECRET_KEY/STRIPE_WEBHOOK_SECRET values is required before
    # this does anything in a real deployment.
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    stripe_checkout_success_url: str = os.getenv(
        "STRIPE_CHECKOUT_SUCCESS_URL", "http://localhost:8080/billing/success"
    )
    stripe_checkout_cancel_url: str = os.getenv("STRIPE_CHECKOUT_CANCEL_URL", "http://localhost:8080/pricing")
    # Stripe price IDs are opaque strings assigned per-project in the Stripe
    # dashboard, so this maps them to this app's own quota tiers via env var
    # rather than hardcoding placeholder IDs: "price_basic:1000,price_pro:100000".
    stripe_price_quota_map: str = os.getenv("STRIPE_PRICE_QUOTA_MAP", "")

    @property
    def stripe_price_to_quota(self) -> dict:
        mapping = {}
        for pair in self.stripe_price_quota_map.split(","):
            if ":" in pair:
                price_id, quota = pair.split(":", 1)
                mapping[price_id.strip()] = int(quota.strip())
        return mapping


settings = Settings()

DEFAULT_SECRET_KEY = "dev-secret-change-me"

if settings.environment == "production" and settings.secret_key == DEFAULT_SECRET_KEY:
    # A production deploy that never overrode SECRET_KEY would otherwise boot
    # fine and silently sign every JWT with a value that's public in this
    # repo's own source — forgeable auth. Fail loudly at import time rather
    # than shipping that.
    raise RuntimeError(
        "SECRET_KEY is still the default development value. Set a real "
        "SECRET_KEY (e.g. `python3 -c \"import secrets; print(secrets.token_urlsafe(48))\"`) "
        "before running with ENVIRONMENT=production."
    )
