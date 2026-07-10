from .helpers import auth_headers, register_and_login


def test_translate_requires_auth(client):
    resp = client.post(
        "/api/v1/translate/",
        json={"text": "hello", "target_lang": "es"},
    )
    assert resp.status_code == 401


def test_translate_placeholder_behavior(client):
    """Locks down the current placeholder so a future real-model swap is a
    deliberate, visible change to this test rather than a silent behavior shift.
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
    assert body["confidence"] == 0.42
    assert body["target_lang"] == "es"
