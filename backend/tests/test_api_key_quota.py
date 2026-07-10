from sqlalchemy import select

from app.models import APIKey

from .conftest import run_db
from .helpers import auth_headers, register_and_login


def _create_api_key(client, token: str):
    resp = client.post("/api/v1/auth/api-keys", headers=auth_headers(token))
    return resp.json()["api_key"]


def test_translate_accepts_api_key_without_jwt(client):
    token = register_and_login(client, "apikey1@example.com")
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
    token = register_and_login(client, "apikey2@example.com")
    key = _create_api_key(client, token)
    client.post(f"/api/v1/auth/api-keys/{key['id']}/revoke", headers=auth_headers(token))

    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": key["key"]},
    )
    assert resp.status_code == 401


def test_api_key_quota_is_enforced(client):
    token = register_and_login(client, "apikey3@example.com")
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
