from typing import Optional

import httpx

from .core.config import settings


class MLServiceError(Exception):
    """Raised when ml-service is unreachable or returns an error."""


class MLServiceClient:
    """Thin HTTP client for the ml-service translation backend.

    Kept as a small, dependency-injectable class (rather than calling httpx
    directly in the route) so tests can override it with a fake in-process
    implementation instead of needing a real model loaded over the network.
    """

    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> dict:
        try:
            resp = httpx.post(
                f"{self.base_url}/translate",
                json={
                    "text": text,
                    "target_lang": target_lang,
                    "source_lang": source_lang,
                    "domain": domain,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise MLServiceError(f"ml-service returned {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise MLServiceError(f"ml-service unreachable: {exc}") from exc
        return resp.json()


def get_ml_client() -> MLServiceClient:
    return MLServiceClient(settings.ml_service_url, settings.ml_service_timeout_seconds)
