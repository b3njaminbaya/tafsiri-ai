from sqlalchemy import select

from app.models import AuthToken

from .conftest import run_db


def _latest_token(purpose: str) -> str:
    async def _impl(db):
        result = await db.execute(
            select(AuthToken).where(AuthToken.purpose == purpose).order_by(AuthToken.id.desc())
        )
        return result.scalars().first()

    return run_db(_impl).token


def test_forgot_password_issues_token_for_existing_user(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "forgot1@example.com", "password": "secret123"},
    )
    resp = client.post("/api/v1/auth/forgot-password", json={"email": "forgot1@example.com"})
    assert resp.status_code == 200
    assert _latest_token("password_reset")


def test_forgot_password_same_response_for_unknown_email(client):
    resp = client.post("/api/v1/auth/forgot-password", json={"email": "nobody@example.com"})
    assert resp.status_code == 200
    assert "message" in resp.json()


def test_reset_password_with_valid_token_changes_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "forgot2@example.com", "password": "oldpassword1"},
    )
    client.post("/api/v1/auth/forgot-password", json={"email": "forgot2@example.com"})
    token = _latest_token("password_reset")

    resp = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "newpassword1"},
    )
    assert resp.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login", data={"username": "forgot2@example.com", "password": "oldpassword1"}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login", data={"username": "forgot2@example.com", "password": "newpassword1"}
    )
    assert new_login.status_code == 200


def test_reset_password_token_is_single_use(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "forgot3@example.com", "password": "oldpassword1"},
    )
    client.post("/api/v1/auth/forgot-password", json={"email": "forgot3@example.com"})
    token = _latest_token("password_reset")

    first = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "newpassword1"}
    )
    assert first.status_code == 200

    second = client.post(
        "/api/v1/auth/reset-password", json={"token": token, "new_password": "anotherpassword1"}
    )
    assert second.status_code == 400


def test_reset_password_rejects_unknown_token(client):
    resp = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-real-token", "new_password": "newpassword1"},
    )
    assert resp.status_code == 400
