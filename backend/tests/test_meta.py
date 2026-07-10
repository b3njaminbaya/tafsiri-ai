def test_languages_endpoint(client):
    resp = client.get("/api/v1/languages")
    assert resp.status_code == 200
    codes = {lang["code"] for lang in resp.json()["languages"]}
    assert "en" in codes


def test_models_endpoint(client):
    resp = client.get("/api/v1/models")
    assert resp.status_code == 200
    models = resp.json()["models"]
    assert models[0]["name"] == "fake-model"
    assert models[0]["loaded"] is True
