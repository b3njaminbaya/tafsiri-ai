def test_explicit_forced_terms_overrides_internal_glossary(client):
    """A caller-supplied forced_terms list is used verbatim, bypassing the
    internal domain glossary lookup entirely — this is what lets the backend
    own a real, DB-backed glossary while ml-service still does the decoding.
    """
    resp = client.post(
        "/translate",
        json={
            "text": "hello world",
            "source_lang": "en",
            "target_lang": "es",
            "forced_terms": ["¡hola personalizada!"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["applied_glossary_terms"] == ["¡hola personalizada!"]
    assert "¡hola personalizada!" in body["translation"]


def test_explicit_empty_forced_terms_skips_internal_glossary(client):
    resp = client.post(
        "/translate",
        json={
            "text": "The doctor wrote a prescription.",
            "source_lang": "en",
            "target_lang": "es",
            "domain": "medical",
            "forced_terms": [],
        },
    )
    assert resp.status_code == 200
    # Without this override, domain=medical would force "receta médica" via
    # the internal glossary (see test_glossary.py) — an explicit empty list
    # must suppress that, not fall back to it.
    assert resp.json()["applied_glossary_terms"] == []


def test_omitted_forced_terms_still_uses_internal_glossary(client):
    resp = client.post(
        "/translate",
        json={
            "text": "The doctor wrote a prescription.",
            "source_lang": "en",
            "target_lang": "es",
            "domain": "medical",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["applied_glossary_terms"] == ["receta médica"]
