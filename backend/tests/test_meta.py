def test_languages_endpoint(client):
    resp = client.get("/api/v1/languages")
    assert resp.status_code == 200
    langs = resp.json()["languages"]
    codes = {lang["code"] for lang in langs}
    assert "en" in codes
    by_code = {lang["code"]: lang for lang in langs}
    assert by_code["sw"]["kenyan"] is True


def test_languages_roadmap_endpoint(client):
    resp = client.get("/api/v1/languages/roadmap")
    assert resp.status_code == 200
    names = {lang["name"] for lang in resp.json()["languages"]}
    assert any("Kikuyu" in name for name in names)


def test_models_endpoint(client):
    resp = client.get("/api/v1/models")
    assert resp.status_code == 200
    models = resp.json()["models"]
    assert models[0]["name"] == "fake-model"
    assert models[0]["loaded"] is True


def test_status_endpoint_reports_all_dependencies_operational(client):
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "operational"
    for dep in ("database", "cache", "storage", "translation_model"):
        assert body["dependencies"][dep]["status"] == "operational"


def test_status_endpoint_reports_ml_service_down(client, monkeypatch):
    from app.ml_client import MLServiceError
    from tests.conftest import _fake_ml

    async def _broken_health(*args, **kwargs):
        raise MLServiceError("simulated outage")

    monkeypatch.setattr(_fake_ml, "get_health", _broken_health)

    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["dependencies"]["translation_model"]["status"] == "down"
    assert body["status"] == "degraded"
