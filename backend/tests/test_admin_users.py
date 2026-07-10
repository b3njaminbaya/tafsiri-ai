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


def test_non_admin_cannot_update_users(client):
    token = register_and_login(client, "admintest_user6@example.com")
    me = client.get("/api/v1/auth/me", headers=auth_headers(token)).json()
    resp = client.patch(
        f"/api/v1/admin/users/{me['id']}",
        json={"role_name": "admin"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 403
