from .helpers import auth_headers, register_and_login


def test_submit_feedback_on_own_translation(client):
    token = register_and_login(client, "feedback_user@example.com")
    headers = auth_headers(token)
    translate_resp = client.post(
        "/api/v1/translate/", json={"text": "hi", "target_lang": "es"}, headers=headers
    )
    translation_id = translate_resp.json()["id"]

    resp = client.post(
        f"/api/v1/translate/{translation_id}/feedback",
        json={"rating": 4, "comment": "Mostly right"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["rating"] == 4
    assert body["comment"] == "Mostly right"
    assert body["translation_id"] == translation_id


def test_cannot_rate_someone_elses_translation(client):
    token_a = register_and_login(client, "owner_fb@example.com")
    token_b = register_and_login(client, "intruder_fb@example.com")
    translate_resp = client.post(
        "/api/v1/translate/",
        json={"text": "hi", "target_lang": "es"},
        headers=auth_headers(token_a),
    )
    translation_id = translate_resp.json()["id"]

    resp = client.post(
        f"/api/v1/translate/{translation_id}/feedback",
        json={"rating": 1},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404


def test_feedback_rating_must_be_in_range(client):
    token = register_and_login(client, "range_user@example.com")
    headers = auth_headers(token)
    translate_resp = client.post(
        "/api/v1/translate/", json={"text": "hi", "target_lang": "es"}, headers=headers
    )
    translation_id = translate_resp.json()["id"]

    resp = client.post(
        f"/api/v1/translate/{translation_id}/feedback",
        json={"rating": 6},
        headers=headers,
    )
    assert resp.status_code == 422
