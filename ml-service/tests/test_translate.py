def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "model_name" in body


def test_languages_is_kenya_only(client):
    resp = client.get("/languages")
    assert resp.status_code == 200
    codes = {lang["code"] for lang in resp.json()["languages"]}
    # This product is Kenya-only: Swahili, Somali, and English (the practical
    # bridge / Kenya's other official language) — nothing else.
    assert codes == {"sw", "so", "en"}


def test_languages_flags_kenyan_codes(client):
    resp = client.get("/languages")
    by_code = {lang["code"]: lang for lang in resp.json()["languages"]}
    assert by_code["sw"]["kenyan"] is True
    assert by_code["so"]["kenyan"] is True
    assert by_code["en"]["kenyan"] is False


def test_languages_roadmap_lists_unsupported_kenyan_languages(client):
    resp = client.get("/languages/roadmap")
    assert resp.status_code == 200
    names = {lang["name"] for lang in resp.json()["languages"]}
    assert any("Kikuyu" in name for name in names)
    assert any("Luo" in name for name in names)
    # None of these should be accepted as an actual source/target — they're
    # a roadmap list, not selectable languages.
    resp = client.post(
        "/translate",
        json={"text": "hi", "source_lang": "en", "target_lang": "ki"},
    )
    assert resp.status_code == 400


def test_translate_with_explicit_source_lang(client):
    resp = client.post(
        "/translate",
        json={"text": "hello world", "source_lang": "en", "target_lang": "sw"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["source_lang"] == "en"
    assert body["target_lang"] == "sw"
    assert isinstance(body["translation"], str) and len(body["translation"]) > 0
    assert 0.0 <= body["confidence"] <= 1.0


def test_translate_auto_detects_source_lang(client):
    resp = client.post(
        "/translate",
        json={"text": "Habari za asubuhi, hali ya hewa ni nzuri leo", "target_lang": "en"},
    )
    assert resp.status_code == 200
    assert resp.json()["source_lang"] == "sw"


def test_translate_rejects_unsupported_language(client):
    resp = client.post(
        "/translate",
        json={"text": "hi", "source_lang": "en", "target_lang": "not-a-real-lang"},
    )
    assert resp.status_code == 400


def test_translate_rejects_whitespace_only_text(client):
    resp = client.post(
        "/translate",
        json={"text": "   ", "source_lang": "en", "target_lang": "sw"},
    )
    assert resp.status_code == 422


def test_translate_short_circuits_same_language(client):
    resp = client.post(
        "/translate",
        json={"text": "hello world", "source_lang": "en", "target_lang": "en"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["translation"] == "hello world"
    assert body["confidence"] == 1.0


def test_translate_auto_detect_failure_returns_400_not_silent_english(client):
    # Too short/ambiguous for langdetect to commit to a language — this must
    # surface as a clear error, not silently translate as if it were English.
    resp = client.post("/translate", json={"text": "xyz123!!", "target_lang": "sw"})
    assert resp.status_code == 400
    assert "source_lang" in resp.json()["detail"]


def test_ready_endpoint_after_model_loaded(client):
    # By this point in the suite other tests have already exercised
    # /translate, so the model is loaded.
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
