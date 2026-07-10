from sqlalchemy import select

from app.models import AuthToken

from .conftest import run_db
from .helpers import auth_headers, register_and_login


def _latest_token(purpose: str) -> str:
    async def _impl(db):
        result = await db.execute(
            select(AuthToken).where(AuthToken.purpose == purpose).order_by(AuthToken.id.desc())
        )
        return result.scalars().first()

    return run_db(_impl).token


def test_new_user_is_unverified_by_default(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "unverified@example.com", "password": "secret123"},
    )
    assert resp.json()["is_verified"] is False


def test_register_issues_verification_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "verifyme@example.com", "password": "secret123"},
    )
    assert _latest_token("email_verification")


def test_verify_email_with_valid_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "verifyme2@example.com", "password": "secret123"},
    )
    token = _latest_token("email_verification")

    resp = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert resp.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        data={"username": "verifyme2@example.com", "password": "secret123"},
    )
    me = client.get("/api/v1/auth/me", headers=auth_headers(login.json()["access_token"]))
    assert me.json()["is_verified"] is True


def test_verify_email_token_is_single_use(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "verifyme3@example.com", "password": "secret123"},
    )
    token = _latest_token("email_verification")
    first = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert first.status_code == 200
    second = client.post("/api/v1/auth/verify-email", json={"token": token})
    assert second.status_code == 400


def test_verify_email_rejects_unknown_token(client):
    resp = client.post("/api/v1/auth/verify-email", json={"token": "not-a-real-token"})
    assert resp.status_code == 400


def test_resend_verification_requires_auth(client):
    resp = client.post("/api/v1/auth/resend-verification")
    assert resp.status_code == 401


def test_resend_verification_issues_new_token(client):
    token = register_and_login(client, "resend@example.com")
    resp = client.post("/api/v1/auth/resend-verification", headers=auth_headers(token))
    assert resp.status_code == 200
    assert _latest_token("email_verification")


def test_resend_verification_noop_if_already_verified(client):
    token = register_and_login(client, "alreadyverified@example.com")
    verify_token = _latest_token("email_verification")
    client.post("/api/v1/auth/verify-email", json={"token": verify_token})

    resp = client.post("/api/v1/auth/resend-verification", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["message"] == "Already verified"
