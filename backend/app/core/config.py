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
