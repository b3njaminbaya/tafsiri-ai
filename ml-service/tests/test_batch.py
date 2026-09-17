def test_batch_translate_same_language_pair(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {"text": "hello", "source_lang": "en", "target_lang": "sw"},
                {"text": "world", "source_lang": "en", "target_lang": "sw"},
                {"text": "goodbye", "source_lang": "en", "target_lang": "sw"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 3
    for r in results:
        assert r["source_lang"] == "en"
        assert r["target_lang"] == "sw"
        assert 0.0 <= r["confidence"] <= 1.0


def test_batch_translate_preserves_order_across_mixed_language_pairs(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {"text": "first", "source_lang": "en", "target_lang": "sw"},
                {"text": "second", "source_lang": "en", "target_lang": "so"},
                {"text": "third", "source_lang": "en", "target_lang": "sw"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert [r["target_lang"] for r in results] == ["sw", "so", "sw"]


def test_batch_translate_applies_glossary_per_item(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {
                    "text": "The doctor wrote a prescription.",
                    "source_lang": "en",
                    "target_lang": "sw",
                    "domain": "medical",
                },
                {"text": "hello", "source_lang": "en", "target_lang": "sw"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results[0]["applied_glossary_terms"] == ["dawa iliyoagizwa"]
    assert "dawa iliyoagizwa" in results[0]["translation"]
    assert results[1]["applied_glossary_terms"] == []


def test_batch_translate_rejects_empty_items(client):
    resp = client.post("/translate/batch", json={"items": []})
    assert resp.status_code == 422


def test_batch_translate_rejects_oversized_batch(client):
    items = [{"text": "hi", "target_lang": "sw"} for _ in range(51)]
    resp = client.post("/translate/batch", json={"items": items})
    assert resp.status_code == 422


def test_batch_translate_rejects_unsupported_language(client):
    resp = client.post(
        "/translate/batch",
        json={"items": [{"text": "hi", "source_lang": "en", "target_lang": "not-real"}]},
    )
    assert resp.status_code == 400


def test_batch_translate_short_circuits_same_language_items(client):
    resp = client.post(
        "/translate/batch",
        json={
            "items": [
                {"text": "first", "source_lang": "en", "target_lang": "so"},
                {"text": "unchanged", "source_lang": "en", "target_lang": "en"},
                {"text": "third", "source_lang": "en", "target_lang": "so"},
            ]
        },
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results[1]["translation"] == "unchanged"
    assert results[1]["confidence"] == 1.0
    assert results[1]["source_lang"] == "en" and results[1]["target_lang"] == "en"
    # The other two items in the same batch still went through real
    # translation and kept their original order.
    assert results[0]["target_lang"] == "so" and results[2]["target_lang"] == "so"
