from .helpers import auth_headers, register_and_login


def test_batch_translate_persists_each_item(client):
    token = register_and_login(client, "batch_user@example.com")
    resp = client.post(
        "/api/v1/translate/batch",
        json={
            "items": [
                {"text": "hello", "target_lang": "es"},
                {"text": "world", "target_lang": "fr"},
            ]
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 2
    assert results[0]["target_lang"] == "es"
    assert results[1]["target_lang"] == "fr"
    assert isinstance(results[0]["id"], int)
    assert results[0]["id"] != results[1]["id"]

    history = client.get("/api/v1/translate/history", headers=auth_headers(token))
    assert len(history.json()) == 2


def test_batch_translate_requires_auth(client):
    resp = client.post(
        "/api/v1/translate/batch",
        json={"items": [{"text": "hi", "target_lang": "es"}]},
    )
    assert resp.status_code == 401


def test_batch_translate_rejects_empty_items(client):
    token = register_and_login(client, "batch_empty@example.com")
    resp = client.post(
        "/api/v1/translate/batch",
        json={"items": []},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


def test_batch_translate_returns_503_when_ml_service_unreachable(client):
    from app.main import app
    from app.ml_client import MLServiceError, get_ml_client

    from .conftest import _fake_ml

    class BrokenMLClient:
        def translate_batch(self, items):
            raise MLServiceError("ml-service unreachable")

    token = register_and_login(client, "batch_broken@example.com")
    app.dependency_overrides[get_ml_client] = lambda: BrokenMLClient()
    try:
        resp = client.post(
            "/api/v1/translate/batch",
            json={"items": [{"text": "hi", "target_lang": "es"}]},
            headers=auth_headers(token),
        )
        assert resp.status_code == 503
    finally:
        app.dependency_overrides[get_ml_client] = lambda: _fake_ml
