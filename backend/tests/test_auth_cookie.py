from .helpers import auth_headers, register_and_login


def test_login_sets_httponly_cookie(client):
    client.post(
        "/api/v1/auth/register", json={"email": "cookieuser@example.com", "password": "secret123"}
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "cookieuser@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "httponly" in set_cookie.lower()


def test_cookie_authenticates_without_explicit_header(client):
    client.post(
        "/api/v1/auth/register", json={"email": "cookieuser2@example.com", "password": "secret123"}
    )
    client.post(
        "/api/v1/auth/login",
        data={"username": "cookieuser2@example.com", "password": "secret123"},
    )
    # No Authorization header at all — the cookie login() set above should be
    # enough. This is the entire point of moving off localStorage.
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "cookieuser2@example.com"


def test_explicit_bearer_header_overrides_ambient_cookie(client):
    token_a = register_and_login(client, "cookie_a@example.com")
    # Logging in as B leaves B's cookie sitting in the client's jar...
    register_and_login(client, "cookie_b@example.com")
    # ...but an explicit Bearer header for A must still authenticate as A.
    resp = client.get("/api/v1/auth/me", headers=auth_headers(token_a))
    assert resp.status_code == 200
    assert resp.json()["email"] == "cookie_a@example.com"


def test_logout_clears_cookie(client):
    client.post(
        "/api/v1/auth/register", json={"email": "logoutuser@example.com", "password": "secret123"}
    )
    client.post(
        "/api/v1/auth/login",
        data={"username": "logoutuser@example.com", "password": "secret123"},
    )
    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 200

    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
