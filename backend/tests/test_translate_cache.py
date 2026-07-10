from .conftest import _fake_ml
from .helpers import auth_headers, register_and_login


def test_identical_translate_requests_hit_cache(client):
    token = register_and_login(client, "cache_user@example.com")
    headers = auth_headers(token)
    payload = {"text": "hello", "target_lang": "es"}

    first = client.post("/api/v1/translate/", json=payload, headers=headers)
    assert first.status_code == 200
    assert first.json()["cached"] is False
    assert _fake_ml.call_count == 1

    second = client.post("/api/v1/translate/", json=payload, headers=headers)
    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert _fake_ml.call_count == 1  # no additional ml-service call on the cache hit

    assert second.json()["translation"] == first.json()["translation"]
    # Each request still gets its own Translation row — caching the model
    # call is an implementation detail, not something that should hide a
    # user's own history of what they translated and when.
    assert second.json()["id"] != first.json()["id"]


def test_different_requests_do_not_share_a_cache_entry(client):
    token = register_and_login(client, "cache_user2@example.com")
    headers = auth_headers(token)

    client.post("/api/v1/translate/", json={"text": "hello", "target_lang": "es"}, headers=headers)
    client.post("/api/v1/translate/", json={"text": "hello", "target_lang": "fr"}, headers=headers)
    assert _fake_ml.call_count == 2
