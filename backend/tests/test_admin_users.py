from sqlalchemy import select

from app.models import Role, User

from .conftest import run_db
from .helpers import auth_headers, register_and_login


def test_non_admin_cannot_list_users(client):
    token = register_and_login(client, "admintest_user1@example.com")
    resp = client.get("/api/v1/admin/users", headers=auth_headers(token))
    assert resp.status_code == 403


def test_admin_can_list_users(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_admin1@example.com")
    register_and_login(client, "admintest_user2@example.com")

    resp = client.get("/api/v1/admin/users", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert "admintest_admin1@example.com" in emails
    assert "admintest_user2@example.com" in emails


def test_admin_can_change_a_users_role(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_admin2@example.com")
    target_token = register_and_login(client, "admintest_user3@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(target_token)).json()

    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "translator"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["role"]["name"] == "translator"


def test_admin_can_deactivate_another_user(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_admin3@example.com")
    target_token = register_and_login(client, "admintest_user4@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(target_token)).json()

    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_admin_cannot_deactivate_self(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_admin4@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(admin_token)).json()

    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_update_unknown_user_returns_404(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_admin5@example.com")
    resp = client.patch(
        "/api/v1/admin/users/999999",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404


def test_update_with_unknown_role_rejected(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_admin6@example.com")
    target_token = register_and_login(client, "admintest_user5@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(target_token)).json()

    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "superuser"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 422


def test_last_admin_cannot_demote_self(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admintest_lastadmin@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(admin_token)).json()

    # The shared test DB accumulates admins created by other tests in this
    # module (promote_actor_to_admin writes directly to the DB, bypassing
    # this endpoint's own guard) — deactivate every other admin so this one
    # is genuinely the last, to exercise the guard deterministically.
    async def _isolate_as_only_admin(db):
        admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
        others = (
            (
                await db.execute(
                    select(User).where(User.role_id == admin_role.id, User.id != me["id"])
                )
            )
            .scalars()
            .all()
        )
        for other in others:
            other.is_active = False
        await db.commit()

    run_db(_isolate_as_only_admin)

    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "user"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_non_last_admin_can_demote_self(client, promote_actor_to_admin):
    admin_token_a = promote_actor_to_admin("admintest_demote_a@example.com")
    promote_actor_to_admin("admintest_demote_b@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(admin_token_a)).json()

    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "user"},
        headers=auth_headers(admin_token_a),
    )
    assert resp.status_code == 200
    assert resp.json()["role"]["name"] == "user"


def test_non_admin_cannot_update_users(client):
    token = register_and_login(client, "admintest_user6@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(token)).json()
    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "admin"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 403
