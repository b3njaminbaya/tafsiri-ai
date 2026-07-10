from .helpers import auth_headers, register_and_login


def test_register_creates_user_with_default_role(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["role"]["name"] == "user"


def test_register_duplicate_email_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dupe@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "dupe@example.com", "password": "another123"},
    )
    assert resp.status_code == 400


def test_login_success_and_failure(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "secret123"},
    )
    ok = client.post(
        "/api/v1/auth/login",
        data={"username": "bob@example.com", "password": "secret123"},
    )
    assert ok.status_code == 200
    assert ok.json()["token_type"] == "bearer"
    assert ok.json()["access_token"]

    bad = client.post(
        "/api/v1/auth/login",
        data={"username": "bob@example.com", "password": "wrong-password"},
    )
    assert bad.status_code == 401


def test_me_requires_valid_token(client):
    token = register_and_login(client, "carol@example.com")
    ok = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert ok.status_code == 200
    assert ok.json()["email"] == "carol@example.com"

    # login() also sets an httpOnly auth cookie (see test_auth_cookie.py) —
    # clear it here so these checks test "truly no credentials" rather than
    # falling back to carol's still-valid ambient cookie from the line above.
    client.cookies.clear()

    no_token = client.get("/api/v1/auth/me")
    assert no_token.status_code == 401

    bad_token = client.get("/api/v1/auth/me", headers=auth_headers("not-a-real-token"))
    assert bad_token.status_code == 401


def test_update_display_name(client):
    token = register_and_login(client, "dana@example.com")

    resp = client.patch(
        "/api/v1/auth/me", json={"display_name": "Dana"}, headers=auth_headers(token)
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Dana"

    me = client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert me.json()["display_name"] == "Dana"

    # Blank clears it back to no display name (falls back to email locally elsewhere)
    cleared = client.patch(
        "/api/v1/auth/me", json={"display_name": "  "}, headers=auth_headers(token)
    )
    assert cleared.status_code == 200
    assert cleared.json()["display_name"] is None
