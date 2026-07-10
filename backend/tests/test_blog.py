from .helpers import auth_headers, register_and_login


def test_public_list_is_empty_by_default(client):
    resp = client.get("/api/v1/blog/posts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_non_admin_cannot_create_post(client):
    token = register_and_login(client, "blog_user1@example.com")
    resp = client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "Hello", "body": "World"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_admin_create_draft_not_publicly_visible(client, promote_actor_to_admin):
    token = promote_actor_to_admin("blog-admin1@example.com")
    create = client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "My Draft Post", "body": "Not ready yet."},
        headers=auth_headers(token),
    )
    assert create.status_code == 200
    body = create.json()
    assert body["status"] == "draft"
    assert body["slug"] == "my-draft-post"
    assert body["published_at"] is None

    public = client.get("/api/v1/blog/posts")
    assert public.json() == []

    public_detail = client.get(f"/api/v1/blog/posts/{body['slug']}")
    assert public_detail.status_code == 404

    admin_detail = client.get(f"/api/v1/blog/admin/posts/{body['id']}", headers=auth_headers(token))
    assert admin_detail.status_code == 200
    assert admin_detail.json()["body"] == "Not ready yet."


def test_admin_create_and_publish_post_flow(client, promote_actor_to_admin):
    token = promote_actor_to_admin("blog-admin2@example.com")
    create = client.post(
        "/api/v1/blog/admin/posts",
        json={
            "title": "Announcing Swahili Support",
            "excerpt": "Big news",
            "body": "Full article body here.",
            "category": "product",
            "status": "published",
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 200
    body = create.json()
    assert body["status"] == "published"
    assert body["published_at"] is not None
    slug = body["slug"]

    public_list = client.get("/api/v1/blog/posts")
    assert any(p["slug"] == slug for p in public_list.json())

    public_detail = client.get(f"/api/v1/blog/posts/{slug}")
    assert public_detail.status_code == 200
    assert public_detail.json()["body"] == "Full article body here."


def test_duplicate_titles_get_distinct_slugs(client, promote_actor_to_admin):
    token = promote_actor_to_admin("blog-admin3@example.com")
    first = client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "Same Title", "body": "First"},
        headers=auth_headers(token),
    )
    second = client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "Same Title", "body": "Second"},
        headers=auth_headers(token),
    )
    assert first.json()["slug"] == "same-title"
    assert second.json()["slug"] == "same-title-2"


def test_admin_can_update_and_publish_existing_post(client, promote_actor_to_admin):
    token = promote_actor_to_admin("blog-admin4@example.com")
    create = client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "Draft To Publish", "body": "v1"},
        headers=auth_headers(token),
    )
    post_id = create.json()["id"]

    update = client.patch(
        f"/api/v1/blog/admin/posts/{post_id}",
        json={"body": "v2", "status": "published"},
        headers=auth_headers(token),
    )
    assert update.status_code == 200
    assert update.json()["body"] == "v2"
    assert update.json()["status"] == "published"
    assert update.json()["published_at"] is not None

    unpublish = client.patch(
        f"/api/v1/blog/admin/posts/{post_id}",
        json={"status": "draft"},
        headers=auth_headers(token),
    )
    assert unpublish.json()["status"] == "draft"
    assert unpublish.json()["published_at"] is None


def test_admin_can_delete_post(client, promote_actor_to_admin):
    token = promote_actor_to_admin("blog-admin5@example.com")
    create = client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "To Delete", "body": "bye"},
        headers=auth_headers(token),
    )
    post_id = create.json()["id"]

    delete = client.delete(f"/api/v1/blog/admin/posts/{post_id}", headers=auth_headers(token))
    assert delete.status_code == 200

    admin_list = client.get("/api/v1/blog/admin/posts", headers=auth_headers(token))
    assert all(p["id"] != post_id for p in admin_list.json())


def test_admin_list_includes_drafts_and_published(client, promote_actor_to_admin):
    token = promote_actor_to_admin("blog-admin6@example.com")
    client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "Draft One", "body": "b"},
        headers=auth_headers(token),
    )
    client.post(
        "/api/v1/blog/admin/posts",
        json={"title": "Published One", "body": "b", "status": "published"},
        headers=auth_headers(token),
    )
    resp = client.get("/api/v1/blog/admin/posts", headers=auth_headers(token))
    statuses = {p["title"]: p["status"] for p in resp.json()}
    assert statuses["Draft One"] == "draft"
    assert statuses["Published One"] == "published"
