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
        json={"email": "dupe@example.com", "password": "another"},
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

    no_token = client.get("/api/v1/auth/me")
    assert no_token.status_code == 401

    bad_token = client.get("/api/v1/auth/me", headers=auth_headers("not-a-real-token"))
    assert bad_token.status_code == 401
