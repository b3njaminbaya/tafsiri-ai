from app.cache import CacheClient


class _ExplodingRedis:
    def get(self, key):
        raise RuntimeError("redis is down")

    def set(self, key, value, ex=None):
        raise RuntimeError("redis is down")


def test_translation_key_is_deterministic_and_distinguishes_inputs():
    k1 = CacheClient.translation_key("hello", "en", "es", None)
    k2 = CacheClient.translation_key("hello", "en", "es", None)
    k3 = CacheClient.translation_key("hello", "en", "fr", None)
    k4 = CacheClient.translation_key("hello", "en", "es", "medical")
    assert k1 == k2
    assert k1 != k3
    assert k1 != k4


def test_cache_get_degrades_to_none_on_redis_error():
    cache = CacheClient("redis://localhost:6379/0", 3600)
    cache._client = _ExplodingRedis()
    assert cache.get("some-key") is None


def test_cache_set_swallows_redis_error():
    cache = CacheClient("redis://localhost:6379/0", 3600)
    cache._client = _ExplodingRedis()
    cache.set("some-key", {"a": 1})  # must not raise
