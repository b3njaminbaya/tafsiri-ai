def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model_name" in body


def test_languages_includes_low_resource_coverage(client):
    resp = client.get("/languages")
    assert resp.status_code == 200
    codes = {lang["code"] for lang in resp.json()["languages"]}
    # This product's differentiator: real coverage for languages mainstream
    # translation APIs underserve, not just the usual major-language demo set.
    for code in ("sw", "am", "ha", "yo", "zu"):
        assert code in codes


def test_translate_with_explicit_source_lang(client):
    resp = client.post(
        "/translate",
        json={"text": "hello world", "source_lang": "en", "target_lang": "es"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["source_lang"] == "en"
    assert body["target_lang"] == "es"
    assert isinstance(body["translation"], str) and len(body["translation"]) > 0
    assert 0.0 <= body["confidence"] <= 1.0


def test_translate_auto_detects_source_lang(client):
    resp = client.post(
        "/translate",
        json={"text": "Bonjour le monde, comment ça va aujourd'hui", "target_lang": "en"},
    )
    assert resp.status_code == 200
    assert resp.json()["source_lang"] == "fr"


def test_translate_rejects_unsupported_language(client):
    resp = client.post(
        "/translate",
        json={"text": "hi", "source_lang": "en", "target_lang": "not-a-real-lang"},
    )
    assert resp.status_code == 400
