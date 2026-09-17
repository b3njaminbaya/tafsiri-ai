from .helpers import auth_headers, register_and_login


def test_regular_user_cannot_promote(client):
    actor_token = register_and_login(client, "actor@example.com")
    target_token = register_and_login(client, "target@example.com")

    target_id = client.get("/api/v1/auth/me", headers=auth_headers(target_token)).json()["id"]

    resp = client.patch(
        f"/api/v1/admin/users/{target_id}",
        json={"role_name": "translator"},
        headers=auth_headers(actor_token),
    )
    assert resp.status_code == 403


def test_promote_unknown_user_returns_404_for_admin(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("admin_user@example.com")
    resp = client.patch(
        "/api/v1/admin/users/999999",
        json={"role_name": "translator"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 404
