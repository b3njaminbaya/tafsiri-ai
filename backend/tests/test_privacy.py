from .helpers import auth_headers, register_and_login, register_login_and_verify


def test_default_privacy_settings(client):
    token = register_and_login(client, "privacy1@example.com")
    resp = client.get("/api/v1/privacy/settings", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["analytics"] is True
    assert body["marketing"] is False


def test_update_privacy_settings_persists(client):
    token = register_and_login(client, "privacy2@example.com")
    headers = auth_headers(token)

    update = client.put(
        "/api/v1/privacy/settings",
        json={"marketing": True, "location_tracking": True},
        headers=headers,
    )
    assert update.status_code == 200
    assert update.json()["marketing"] is True
    assert update.json()["location_tracking"] is True
    # Untouched fields keep their existing values.
    assert update.json()["analytics"] is True

    fetched = client.get("/api/v1/privacy/settings", headers=headers)
    assert fetched.json()["marketing"] is True


def test_privacy_settings_requires_auth(client):
    resp = client.get("/api/v1/privacy/settings")
    assert resp.status_code == 401


def test_export_includes_own_translations_and_not_other_users(client):
    token_a = register_and_login(client, "export_a@example.com")
    token_b = register_and_login(client, "export_b@example.com")
    client.post(
        "/api/v1/translate/", json={"text": "mine", "target_lang": "es"}, headers=auth_headers(token_a)
    )
    client.post(
        "/api/v1/translate/",
        json={"text": "not mine", "target_lang": "es"},
        headers=auth_headers(token_b),
    )

    resp = client.get("/api/v1/privacy/export", headers=auth_headers(token_a))
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["email"] == "export_a@example.com"
    assert len(body["translations"]) == 1
    assert body["translations"][0]["input_text"] == "mine"


def test_delete_account_anonymizes_and_deactivates(client):
    token = register_login_and_verify(client, "deleteme@example.com")
    headers = auth_headers(token)
    client.post("/api/v1/auth/api-keys", headers=headers)

    resp = client.post("/api/v1/privacy/delete-account", headers=headers)
    assert resp.status_code == 200

    # The old token is now for a deactivated user — further requests using it
    # (even the still-valid JWT) must be rejected.
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 400

    # The original email is free to register again.
    register_again = client.post(
        "/api/v1/auth/register",
        json={"email": "deleteme@example.com", "password": "secret123"},
    )
    assert register_again.status_code == 200


def test_delete_account_revokes_api_keys(client):
    token = register_login_and_verify(client, "deleteme2@example.com")
    headers = auth_headers(token)
    created = client.post("/api/v1/auth/api-keys", headers=headers)
    key_value = created.json()["key"]

    client.post("/api/v1/privacy/delete-account", headers=headers)

    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers={"X-API-Key": key_value},
    )
    assert resp.status_code == 401


def test_gdpr_access_request_auto_completes(client):
    token = register_and_login(client, "gdpr1@example.com")
    resp = client.post(
        "/api/v1/privacy/gdpr-requests",
        json={"request_type": "access"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert resp.json()["resolved_at"] is not None


def test_gdpr_rectification_request_stays_pending(client):
    token = register_and_login(client, "gdpr2@example.com")
    resp = client.post(
        "/api/v1/privacy/gdpr-requests",
        json={"request_type": "rectification", "description": "Fix my name"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"
    assert resp.json()["resolved_at"] is None


def test_gdpr_request_rejects_invalid_type(client):
    token = register_and_login(client, "gdpr3@example.com")
    resp = client.post(
        "/api/v1/privacy/gdpr-requests",
        json={"request_type": "not-a-real-type"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


def test_list_gdpr_requests_scoped_to_user(client):
    token_a = register_and_login(client, "gdpr4a@example.com")
    token_b = register_and_login(client, "gdpr4b@example.com")
    client.post(
        "/api/v1/privacy/gdpr-requests",
        json={"request_type": "access"},
        headers=auth_headers(token_a),
    )

    listing_b = client.get("/api/v1/privacy/gdpr-requests", headers=auth_headers(token_b))
    assert listing_b.json() == []

    listing_a = client.get("/api/v1/privacy/gdpr-requests", headers=auth_headers(token_a))
    assert len(listing_a.json()) == 1
