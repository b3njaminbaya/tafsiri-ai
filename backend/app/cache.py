import hashlib
import json
import logging
from typing import Optional

import redis

from .core.config import settings

logger = logging.getLogger("app.cache")


class CacheClient:
    """Thin Redis wrapper for caching repeated translation requests — a real,
    common production win (translating the same string twice is common
    traffic), not just a checkbox. Caching is an optimization, not a
    correctness requirement: any Redis error is logged and treated as a cache
    miss/no-op rather than failing the request.
    """

    def __init__(self, redis_url: str, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._client = redis.Redis.from_url(
            redis_url, decode_responses=True, socket_connect_timeout=1, socket_timeout=1
        )

    @staticmethod
    def translation_key(
        text: str, source_lang: Optional[str], target_lang: str, domain: Optional[str]
    ) -> str:
        raw = f"{source_lang or 'auto'}|{target_lang}|{domain or ''}|{text}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"translate:{digest}"

    def get(self, key: str) -> Optional[dict]:
        try:
            raw = self._client.get(key)
        except Exception as exc:
            logger.warning("Cache get failed, treating as a miss: %s", exc)
            return None
        return json.loads(raw) if raw else None

    def set(self, key: str, value: dict) -> None:
        try:
            self._client.set(key, json.dumps(value), ex=self.ttl_seconds)
        except Exception as exc:
            logger.warning("Cache set failed, continuing without caching: %s", exc)

    def ping(self) -> bool:
        """Used by GET /status to report real Redis reachability, distinct
        from get()/set() which always degrade silently to a no-op.
        """
        try:
            return bool(self._client.ping())
        except Exception:
            return False


def get_cache_client() -> CacheClient:
    return CacheClient(settings.redis_url, settings.cache_ttl_seconds)
