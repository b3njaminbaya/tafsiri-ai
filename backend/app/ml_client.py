from typing import List, Optional, TypedDict

import httpx

from .core.config import settings


class TranslateItem(TypedDict, total=False):
    text: str
    target_lang: str
    source_lang: Optional[str]
    domain: Optional[str]
    forced_terms: Optional[List[str]]


class MLServiceError(Exception):
    """Raised when ml-service is unreachable or returns an error."""


class MLServiceClient:
    """Thin async HTTP client for the ml-service translation backend.

    Kept as a small, dependency-injectable class (rather than calling httpx
    directly in the route) so tests can override it with a fake in-process
    implementation instead of needing a real model loaded over the network.
    Async so a slow/hanging ml-service call doesn't block the event loop out
    from under every other concurrent request the API is serving.
    """

    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None,
        domain: Optional[str] = None,
        forced_terms: Optional[List[str]] = None,
    ) -> dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/translate",
                    json={
                        "text": text,
                        "target_lang": target_lang,
                        "source_lang": source_lang,
                        "domain": domain,
                        "forced_terms": forced_terms,
                    },
                )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise MLServiceError(f"ml-service returned {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise MLServiceError(f"ml-service unreachable: {exc}") from exc
        return resp.json()

    async def get_languages(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/languages")
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MLServiceError(f"ml-service unreachable: {exc}") from exc
        return resp.json()

    async def get_health(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/health")
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise MLServiceError(f"ml-service unreachable: {exc}") from exc
        return resp.json()

    async def translate_batch(self, items: List[TranslateItem]) -> List[dict]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/translate/batch",
                    json={"items": items},
                )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise MLServiceError(f"ml-service returned {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise MLServiceError(f"ml-service unreachable: {exc}") from exc
        return resp.json()["results"]


def get_ml_client() -> MLServiceClient:
    return MLServiceClient(settings.ml_service_url, settings.ml_service_timeout_seconds)
