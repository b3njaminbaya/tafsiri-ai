from .helpers import auth_headers, register_and_login


def test_translate_requires_auth(client):
    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hello", "target_lang": "es"},
    )
    assert resp.status_code == 401


def test_translate_persists_and_returns_result(client):
    """Exercises the real route wired to FakeMLClient (conftest.py) — proves
    the persistence path, not any particular model's output.
    """
    token = register_and_login(client, "translator_user@example.com")
    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hello", "target_lang": "es"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["translation"] == "[es] olleh"
    assert body["confidence"] == 0.87
    assert body["target_lang"] == "es"
    assert isinstance(body["id"], int)


def test_translate_history_lists_own_translations_most_recent_first(client):
    token = register_and_login(client, "history_user@example.com")
    headers = auth_headers(token)
    client.post("/api/v1/translate/", json={"text": "first", "target_lang": "es"}, headers=headers)
    client.post("/api/v1/translate/", json={"text": "second", "target_lang": "fr"}, headers=headers)

    history = client.get("/api/v1/translate/history", headers=headers)
    assert history.status_code == 200
    body = history.json()
    assert len(body) == 2
    assert body[0]["input_text"] == "second"
    assert body[1]["input_text"] == "first"


def test_translate_history_is_scoped_to_current_user(client):
    token_a = register_and_login(client, "history_a@example.com")
    token_b = register_and_login(client, "history_b@example.com")
    client.post(
        "/api/v1/translate/",
        json={"text": "mine", "target_lang": "es"},
        headers=auth_headers(token_a),
    )

    history_b = client.get("/api/v1/translate/history", headers=auth_headers(token_b))
    assert history_b.status_code == 200
    assert history_b.json() == []
