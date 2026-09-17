from sqlalchemy import select

from app.models import APIKey

from .conftest import run_db
from .helpers import auth_headers, register_and_login, register_login_and_verify


def _create_api_key(client, token: str):
    resp = client.post("/api/v1/auth/api-keys", headers=auth_headers(token))
    body = resp.json()
    # Merge the one-time raw secret into the returned dict under "key" so
    # existing call sites (`key["key"]`, `key["id"]`) keep working — the API
    # itself only returns the raw value at the top level, alongside the
    # masked api_key object, exactly once.
    return {**body["api_key"], "key": body["key"]}


def test_translate_accepts_api_key_without_jwt(client):
    token = register_login_and_verify(client, "apikey1@example.com")
    key = _create_api_key(client, token)

    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": key["key"]},
    )
    assert resp.status_code == 200
    assert resp.json()["translation"] == "[es] ih"


def test_translate_rejects_unknown_api_key(client):
    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": "not-a-real-key"},
    )
    assert resp.status_code == 401


def test_translate_rejects_revoked_api_key(client):
    token = register_login_and_verify(client, "apikey2@example.com")
    key = _create_api_key(client, token)
    client.post(f"/api/v1/auth/api-keys/{key['id']}/revoke", headers=auth_headers(token))

    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": key["key"]},
    )
    assert resp.status_code == 401


def test_api_key_quota_is_enforced(client):
    token = register_login_and_verify(client, "apikey3@example.com")
    key = _create_api_key(client, token)

    # No API endpoint sets quota_limit yet, so we reach into the DB directly —
    # same rationale as the admin-promotion test fixture.
    async def _set_quota(db):
        db_key = (await db.execute(select(APIKey).where(APIKey.id == key["id"]))).scalar_one()
        db_key.quota_limit = 1
        await db.commit()

    run_db(_set_quota)

    ok = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": key["key"]},
    )
    assert ok.status_code == 200

    blocked = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": key["key"]},
    )
    assert blocked.status_code == 429


def test_api_key_quota_not_charged_on_cache_hit(client):
    token = register_login_and_verify(client, "apikey4@example.com")
    key = _create_api_key(client, token)

    async def _set_quota(db):
        db_key = (await db.execute(select(APIKey).where(APIKey.id == key["id"]))).scalar_one()
        db_key.quota_limit = 2
        await db.commit()

    run_db(_set_quota)

    payload = {"text": "hi", "target_lang": "es"}
    first = client.post("/api/v1/translate/", json=payload, headers={"X-API-Key": key["key"]})
    assert first.status_code == 200
    assert first.json()["cached"] is False

    # Same (text, source_lang, target_lang, domain) — served from cache, so
    # it must not consume a second quota unit.
    second = client.post("/api/v1/translate/", json=payload, headers={"X-API-Key": key["key"]})
    assert second.status_code == 200
    assert second.json()["cached"] is True

    async def _get_used(db):
        db_key = (await db.execute(select(APIKey).where(APIKey.id == key["id"]))).scalar_one()
        return db_key.quota_used

    assert run_db(_get_used) == 1


def test_api_key_quota_refunded_on_ml_service_failure(client, monkeypatch):
    token = register_login_and_verify(client, "apikey5@example.com")
    key = _create_api_key(client, token)

    async def _set_quota(db):
        db_key = (await db.execute(select(APIKey).where(APIKey.id == key["id"]))).scalar_one()
        db_key.quota_limit = 5
        await db.commit()

    run_db(_set_quota)

    from app.ml_client import MLServiceError
    from tests.conftest import _fake_ml

    async def _broken_translate(*args, **kwargs):
        raise MLServiceError("simulated ml-service outage")

    monkeypatch.setattr(_fake_ml, "translate", _broken_translate)

    resp = client.post(
        "/api/v1/translate/",
        json={"text": "unique text for failure test", "target_lang": "es"},
        headers={"X-API-Key": key["key"]},
    )
    assert resp.status_code == 503

    async def _get_used(db):
        db_key = (await db.execute(select(APIKey).where(APIKey.id == key["id"]))).scalar_one()
        return db_key.quota_used

    assert run_db(_get_used) == 0
