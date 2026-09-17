def register_and_login(client, email: str, password: str = "secret123") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return login.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def verify_email(email: str) -> None:
    """Marks a user verified directly in the test DB — used by tests that
    need a verified account (e.g. to create an API key, see
    auth.py:create_api_key) but aren't themselves testing the verification
    flow, the same "reach into the DB directly" pattern conftest.py's
    promote_actor_to_admin fixture uses for role promotion.
    """
    from sqlalchemy import select

    from app.models import User

    from .conftest import run_db

    async def _verify(db):
        user = (await db.execute(select(User).where(User.email == email))).scalar_one()
        user.is_verified = True
        await db.commit()

    run_db(_verify)


def register_login_and_verify(client, email: str, password: str = "secret123") -> str:
    token = register_and_login(client, email, password)
    verify_email(email)
    return token
