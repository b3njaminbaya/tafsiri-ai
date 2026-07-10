from .helpers import auth_headers, register_and_login


def test_list_posts_empty_by_default(client):
    resp = client.get("/api/v1/forum/posts")
    assert resp.status_code == 200
    assert resp.json() == []


def test_categories_start_at_zero(client):
    resp = client.get("/api/v1/forum/categories")
    assert resp.status_code == 200
    body = resp.json()
    assert {c["category"] for c in body} == {
        "general",
        "technical",
        "feature_requests",
        "model_training",
        "dataset_sharing",
    }
    assert all(c["post_count"] == 0 for c in body)


def test_unauthenticated_cannot_create_post(client):
    resp = client.post(
        "/api/v1/forum/posts",
        json={"category": "general", "title": "Hello", "body": "First post"},
    )
    assert resp.status_code == 401


def test_invalid_category_rejected(client):
    token = register_and_login(client, "forum_user1@example.com")
    resp = client.post(
        "/api/v1/forum/posts",
        json={"category": "not-a-real-category", "title": "Hello", "body": "First post"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


def test_create_list_and_view_post_with_replies(client):
    author_token = register_and_login(client, "forum_author@example.com")
    create = client.post(
        "/api/v1/forum/posts",
        json={
            "category": "technical",
            "title": "API rate limits?",
            "body": "What's the default quota per key?",
        },
        headers=auth_headers(author_token),
    )
    assert create.status_code == 200
    post = create.json()
    assert post["author_handle"] == "forum_author"
    assert post["reply_count"] == 0
    post_id = post["id"]

    listing = client.get("/api/v1/forum/posts", params={"category": "technical"})
    assert listing.status_code == 200
    assert any(p["id"] == post_id for p in listing.json())

    categories = client.get("/api/v1/forum/categories").json()
    technical_count = next(c["post_count"] for c in categories if c["category"] == "technical")
    assert technical_count == 1

    replier_token = register_and_login(client, "forum_replier@example.com")
    reply = client.post(
        f"/api/v1/forum/posts/{post_id}/replies",
        json={"body": "It's 1000 requests/day by default."},
        headers=auth_headers(replier_token),
    )
    assert reply.status_code == 200
    assert reply.json()["author_handle"] == "forum_replier"

    detail = client.get(f"/api/v1/forum/posts/{post_id}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["title"] == "API rate limits?"
    assert len(detail_body["replies"]) == 1
    assert detail_body["replies"][0]["body"] == "It's 1000 requests/day by default."

    listing_after_reply = client.get("/api/v1/forum/posts").json()
    updated_post = next(p for p in listing_after_reply if p["id"] == post_id)
    assert updated_post["reply_count"] == 1


def test_reply_to_nonexistent_post_returns_404(client):
    token = register_and_login(client, "forum_user2@example.com")
    resp = client.post(
        "/api/v1/forum/posts/999999/replies",
        json={"body": "hello?"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 404


def test_get_nonexistent_post_returns_404(client):
    resp = client.get("/api/v1/forum/posts/999999")
    assert resp.status_code == 404


def test_unauthenticated_cannot_reply(client):
    author_token = register_and_login(client, "forum_author2@example.com")
    create = client.post(
        "/api/v1/forum/posts",
        json={"category": "general", "title": "Hi", "body": "Body"},
        headers=auth_headers(author_token),
    )
    post_id = create.json()["id"]

    # login() also sets an httpOnly auth cookie — clear it so this checks
    # "truly no credentials" rather than falling back to the still-valid
    # ambient cookie from register_and_login() above.
    client.cookies.clear()

    resp = client.post(f"/api/v1/forum/posts/{post_id}/replies", json={"body": "hi"})
    assert resp.status_code == 401
