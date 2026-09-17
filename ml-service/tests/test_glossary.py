from app.glossary import find_glossary_terms


def test_find_glossary_terms_matches_whole_words():
    terms = find_glossary_terms("medical", "en", "sw", "Please review the prescription carefully.")
    assert terms == ["dawa iliyoagizwa"]


def test_find_glossary_terms_no_match_without_domain():
    assert find_glossary_terms(None, "en", "sw", "Please review the prescription.") == []


def test_find_glossary_terms_no_partial_word_match():
    # "prescriptions" (plural) shouldn't match the "prescription" glossary entry
    # via substring — only whole-word matches count.
    terms = find_glossary_terms("medical", "en", "sw", "prescriptionist")
    assert terms == []


def test_translate_forces_glossary_term_into_output(client):
    """force_words_ids guarantees the forced token sequence appears in the
    decoded output regardless of model quality — this holds even for the tiny
    random-weight test model, which is what makes it a meaningful assertion
    here rather than a check that depends on real translation quality.
    """
    resp = client.post(
        "/translate",
        json={
            "text": "The doctor wrote a prescription.",
            "source_lang": "en",
            "target_lang": "sw",
            "domain": "medical",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["applied_glossary_terms"] == ["dawa iliyoagizwa"]
    assert "dawa iliyoagizwa" in body["translation"]


def test_translate_without_domain_applies_no_glossary(client):
    resp = client.post(
        "/translate",
        json={"text": "The doctor wrote a prescription.", "source_lang": "en", "target_lang": "sw"},
    )
    assert resp.status_code == 200
    assert resp.json()["applied_glossary_terms"] == []
