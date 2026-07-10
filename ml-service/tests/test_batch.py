def test_batch_translate_same_language_pair(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {"text": "hello", "source_lang": "en", "target_lang": "es"},
                {"text": "world", "source_lang": "en", "target_lang": "es"},
                {"text": "goodbye", "source_lang": "en", "target_lang": "es"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 3
    for r in results:
        assert r["source_lang"] == "en"
        assert r["target_lang"] == "es"
        assert 0.0 <= r["confidence"] <= 1.0


def test_batch_translate_preserves_order_across_mixed_language_pairs(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {"text": "first", "source_lang": "en", "target_lang": "es"},
                {"text": "second", "source_lang": "en", "target_lang": "fr"},
                {"text": "third", "source_lang": "en", "target_lang": "es"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert [r["target_lang"] for r in results] == ["es", "fr", "es"]


def test_batch_translate_applies_glossary_per_item(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {
                    "text": "The doctor wrote a prescription.",
                    "source_lang": "en",
                    "target_lang": "es",
                    "domain": "medical",
                },
                {"text": "hello", "source_lang": "en", "target_lang": "es"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results[0]["applied_glossary_terms"] == ["receta médica"]
    assert "receta médica" in results[0]["translation"]
    assert results[1]["applied_glossary_terms"] == []


def test_batch_translate_rejects_empty_items(client):
    resp = client.post("/translate/batch", json={"items": []})
    assert resp.status_code == 422


def test_batch_translate_rejects_oversized_batch(client):
    items = [{"text": "hi", "target_lang": "es"} for _ in range(51)]
    resp = client.post("/translate/batch", json={"items": items})
    assert resp.status_code == 422


def test_batch_translate_rejects_unsupported_language(client):
    resp = client.post(
        "/translate/batch",
        json={"items": [{"text": "hi", "source_lang": "en", "target_lang": "not-real"}]},
    )
    assert resp.status_code == 400
