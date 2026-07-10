import re

from app.models import User
from sqlalchemy import select

from .conftest import _fake_github_oauth, _fake_google_oauth, run_db
from .helpers import register_and_login


def test_providers_reports_configured_state(client):
    resp = client.get("/api/v1/auth/oauth/providers")
    assert resp.status_code == 200
    assert resp.json() == {"google": True, "github": True}


def test_providers_reports_unconfigured_state(client):
    _fake_google_oauth.configured = False
    resp = client.get("/api/v1/auth/oauth/providers")
    assert resp.json()["google"] is False
    assert resp.json()["github"] is True


def test_login_redirects_to_provider_and_sets_state_cookie(client):
    resp = client.get("/api/v1/auth/oauth/google/login", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers["location"].startswith("https://fake-google.local/authorize?state=")
    assert "oauth_state=" in resp.headers.get("set-cookie", "")


def test_login_returns_503_when_provider_not_configured(client):
    _fake_github_oauth.configured = False
    resp = client.get("/api/v1/auth/oauth/github/login")
    assert resp.status_code == 503


def test_callback_creates_new_user_and_authenticates(client):
    _fake_google_oauth.next_email = "newoauthuser@example.com"
    _fake_google_oauth.next_subject = "google-subject-42"

    login_resp = client.get("/api/v1/auth/oauth/google/login", follow_redirects=False)
    state = re.search(r"state=([^&]+)", login_resp.headers["location"]).group(1)

    callback = client.get(
        f"/api/v1/auth/oauth/google/callback?code=good-code&state={state}",
        follow_redirects=False,
    )
    assert callback.status_code in (302, 307)
    assert callback.headers["location"] == "http://localhost:8080/translate"
    assert "access_token=" in callback.headers.get("set-cookie", "")

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "newoauthuser@example.com"
    assert me.json()["is_verified"] is True


def test_callback_rejects_mismatched_state(client):
    client.get("/api/v1/auth/oauth/google/login", follow_redirects=False)
    resp = client.get(
        "/api/v1/auth/oauth/google/callback?code=good-code&state=not-the-real-state",
        follow_redirects=False,
    )
    assert resp.status_code in (302, 307)
    assert "oauth_error=invalid_state" in resp.headers["location"]
    # No auth cookie should have been issued.
    assert "access_token=" not in resp.headers.get("set-cookie", "")


def test_callback_redirects_with_error_on_provider_failure(client):
    login_resp = client.get("/api/v1/auth/oauth/github/login", follow_redirects=False)
    state = re.search(r"state=([^&]+)", login_resp.headers["location"]).group(1)

    resp = client.get(
        f"/api/v1/auth/oauth/github/callback?code=bad-code&state={state}",
        follow_redirects=False,
    )
    assert resp.status_code in (302, 307)
    assert "oauth_error=failed" in resp.headers["location"]


def test_callback_links_oauth_to_existing_password_account(client):
    register_and_login(client, "linkme@example.com")
    client.cookies.clear()

    _fake_google_oauth.next_email = "linkme@example.com"
    _fake_google_oauth.next_subject = "google-subject-link"

    login_resp = client.get("/api/v1/auth/oauth/google/login", follow_redirects=False)
    state = re.search(r"state=([^&]+)", login_resp.headers["location"]).group(1)
    client.get(
        f"/api/v1/auth/oauth/google/callback?code=good-code&state={state}",
        follow_redirects=False,
    )

    async def _check(db):
        result = await db.execute(select(User).where(User.email == "linkme@example.com"))
        return result.scalar_one()

    linked_user = run_db(_check)
    assert linked_user.oauth_provider == "google"
    assert linked_user.oauth_subject == "google-subject-link"
    # The password-based account still exists as one row, not duplicated.


def test_returning_oauth_user_reuses_same_account(client):
    _fake_google_oauth.next_email = "returning@example.com"
    _fake_google_oauth.next_subject = "google-subject-returning"

    def _do_login():
        login_resp = client.get("/api/v1/auth/oauth/google/login", follow_redirects=False)
        state = re.search(r"state=([^&]+)", login_resp.headers["location"]).group(1)
        client.get(
            f"/api/v1/auth/oauth/google/callback?code=good-code&state={state}",
            follow_redirects=False,
        )

    _do_login()
    first_me = client.get("/api/v1/auth/me").json()
    client.cookies.clear()
    _do_login()
    second_me = client.get("/api/v1/auth/me").json()

    assert first_me["id"] == second_me["id"]


def test_oauth_only_account_cannot_login_with_password(client):
    _fake_google_oauth.next_email = "oauthonly@example.com"
    _fake_google_oauth.next_subject = "google-subject-onlyoauth"

    login_resp = client.get("/api/v1/auth/oauth/google/login", follow_redirects=False)
    state = re.search(r"state=([^&]+)", login_resp.headers["location"]).group(1)
    client.get(
        f"/api/v1/auth/oauth/google/callback?code=good-code&state={state}",
        follow_redirects=False,
    )
    client.cookies.clear()

    resp = client.post(
        "/api/v1/auth/login", data={"username": "oauthonly@example.com", "password": "anything123"}
    )
    assert resp.status_code == 401
