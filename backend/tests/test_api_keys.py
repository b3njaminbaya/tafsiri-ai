from .helpers import auth_headers, register_and_login


def test_api_key_create_list_revoke(client):
    token = register_and_login(client, "dev@example.com")
    headers = auth_headers(token)

    create = client.post("/api/v1/auth/api-keys", headers=headers)
    assert create.status_code == 200
    key = create.json()["api_key"]
    assert key["is_active"] is True
    key_id = key["id"]

    listing = client.get("/api/v1/auth/api-keys", headers=headers)
    assert listing.status_code == 200
    assert any(k["id"] == key_id for k in listing.json())

    revoke = client.post(f"/api/v1/auth/api-keys/{key_id}/revoke", headers=headers)
    assert revoke.status_code == 200

    listing_after = client.get("/api/v1/auth/api-keys", headers=headers)
    revoked_key = next(k for k in listing_after.json() if k["id"] == key_id)
    assert revoked_key["is_active"] is False


def test_revoke_missing_key_returns_404(client):
    token = register_and_login(client, "dev2@example.com")
    resp = client.post("/api/v1/auth/api-keys/999999/revoke", headers=auth_headers(token))
    assert resp.status_code == 404


def test_cannot_revoke_another_users_key(client):
    token_a = register_and_login(client, "owner@example.com")
    token_b = register_and_login(client, "intruder@example.com")

    created = client.post("/api/v1/auth/api-keys", headers=auth_headers(token_a))
    key_id = created.json()["api_key"]["id"]

    resp = client.post(f"/api/v1/auth/api-keys/{key_id}/revoke", headers=auth_headers(token_b))
    assert resp.status_code == 404
