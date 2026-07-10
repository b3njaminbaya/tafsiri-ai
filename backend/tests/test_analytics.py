from .helpers import auth_headers, register_and_login


def test_global_analytics_requires_admin(client, promote_actor_to_admin):
    token = register_and_login(client, "not_an_admin@example.com")
    resp = client.get("/api/v1/analytics/global", headers=auth_headers(token))
    assert resp.status_code == 403

    admin_token = promote_actor_to_admin("global_admin@example.com")
    resp_admin = client.get("/api/v1/analytics/global", headers=auth_headers(admin_token))
    assert resp_admin.status_code == 200
    body = resp_admin.json()
    assert "total_users" in body
    assert "total_datasets" in body


def test_global_analytics_aggregates_across_users(client, promote_actor_to_admin):
    token_a = register_and_login(client, "global_a@example.com")
    token_b = register_and_login(client, "global_b@example.com")
    client.post(
        "/api/v1/translate/", json={"text": "hi", "target_lang": "es"}, headers=auth_headers(token_a)
    )
    client.post(
        "/api/v1/translate/", json={"text": "yo", "target_lang": "fr"}, headers=auth_headers(token_b)
    )

    admin_token = promote_actor_to_admin("global_admin2@example.com")
    resp = client.get("/api/v1/analytics/global", headers=auth_headers(admin_token))
    body = resp.json()
    assert body["total_translations"] >= 2
    assert body["total_users"] >= 3


def test_analytics_requires_auth(client):
    resp = client.get("/api/v1/analytics/summary")
    assert resp.status_code == 401


def test_analytics_reflects_own_translations_only(client):
    token_a = register_and_login(client, "analytics_a@example.com")
    token_b = register_and_login(client, "analytics_b@example.com")

    client.post(
        "/api/v1/translate/", json={"text": "hi", "target_lang": "es"}, headers=auth_headers(token_a)
    )
    client.post(
        "/api/v1/translate/", json={"text": "yo", "target_lang": "fr"}, headers=auth_headers(token_a)
    )
    client.post(
        "/api/v1/translate/", json={"text": "hey", "target_lang": "es"}, headers=auth_headers(token_b)
    )

    resp = client.get("/api/v1/analytics/summary", headers=auth_headers(token_a))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_translations"] == 2
    assert body["average_confidence"] == 0.87

    pairs = {(p["source_lang"], p["target_lang"]): p["count"] for p in body["top_language_pairs"]}
    assert pairs.get(("en", "es")) == 1
    assert pairs.get(("en", "fr")) == 1


def test_analytics_includes_feedback_breakdown(client):
    token = register_and_login(client, "analytics_feedback@example.com")
    headers = auth_headers(token)
    translate_resp = client.post(
        "/api/v1/translate/", json={"text": "hi", "target_lang": "es"}, headers=headers
    )
    translation_id = translate_resp.json()["id"]
    client.post(
        f"/api/v1/translate/{translation_id}/feedback",
        json={"rating": 5},
        headers=headers,
    )

    resp = client.get("/api/v1/analytics/summary", headers=headers)
    breakdown = {r["rating"]: r["count"] for r in resp.json()["feedback_breakdown"]}
    assert breakdown.get(5) == 1


def test_analytics_empty_for_new_user(client):
    token = register_and_login(client, "analytics_empty@example.com")
    resp = client.get("/api/v1/analytics/summary", headers=auth_headers(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_translations"] == 0
    assert body["average_confidence"] == 0.0
    assert body["translations_by_day"] == []
