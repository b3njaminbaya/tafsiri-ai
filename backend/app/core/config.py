from typing import List
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "NMT Agent API"
    environment: str = "development"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/nmt",
    )

    ml_service_url: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ml_service_timeout_seconds: float = float(os.getenv("ML_SERVICE_TIMEOUT_SECONDS", "30"))

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


settings = Settings()
