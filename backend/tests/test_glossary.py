from .helpers import auth_headers, register_and_login


def test_list_glossary_terms_empty_by_default(client):
    resp = client.get("/api/v1/glossary/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_non_admin_cannot_create_glossary_term(client):
    token = register_and_login(client, "translator1@example.com")
    resp = client.post(
        "/api/v1/glossary/",
        json={
            "domain": "medical",
            "source_lang": "en",
            "target_lang": "es",
            "source_term": "prescription",
            "target_term": "receta médica",
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 403


def test_admin_can_create_list_and_delete_glossary_term(client, promote_actor_to_admin):
    token = promote_actor_to_admin("glossary-admin@example.com")
    create = client.post(
        "/api/v1/glossary/",
        json={
            "domain": "medical",
            "source_lang": "en",
            "target_lang": "es",
            "source_term": "prescription",
            "target_term": "receta médica",
        },
        headers=auth_headers(token),
    )
    assert create.status_code == 200
    body = create.json()
    assert body["target_term"] == "receta médica"
    term_id = body["id"]

    listing = client.get(
        "/api/v1/glossary/", params={"domain": "medical", "source_lang": "en", "target_lang": "es"}
    )
    assert listing.status_code == 200
    assert any(t["id"] == term_id for t in listing.json())

    delete = client.delete(f"/api/v1/glossary/{term_id}", headers=auth_headers(token))
    assert delete.status_code == 200

    listing_after = client.get("/api/v1/glossary/", params={"domain": "medical"})
    assert all(t["id"] != term_id for t in listing_after.json())


def test_delete_nonexistent_glossary_term_returns_404(client, promote_actor_to_admin):
    token = promote_actor_to_admin("glossary-admin2@example.com")
    resp = client.delete("/api/v1/glossary/999999", headers=auth_headers(token))
    assert resp.status_code == 404


def test_non_admin_cannot_delete_glossary_term(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("glossary-admin3@example.com")
    create = client.post(
        "/api/v1/glossary/",
        json={
            "domain": "legal",
            "source_lang": "en",
            "target_lang": "fr",
            "source_term": "plaintiff",
            "target_term": "demandeur",
        },
        headers=auth_headers(admin_token),
    )
    term_id = create.json()["id"]

    other_token = register_and_login(client, "translator2@example.com")
    resp = client.delete(f"/api/v1/glossary/{term_id}", headers=auth_headers(other_token))
    assert resp.status_code == 403


def test_translate_applies_matching_glossary_terms(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("glossary-admin4@example.com")
    client.post(
        "/api/v1/glossary/",
        json={
            "domain": "medical",
            "source_lang": "en",
            "target_lang": "es",
            "source_term": "dosage",
            "target_term": "dosis",
        },
        headers=auth_headers(admin_token),
    )

    user_token = register_and_login(client, "glossary-user@example.com")
    resp = client.post(
        "/api/v1/translate/",
        json={
            "text": "Confirm the dosage before dispensing.",
            "source_lang": "en",
            "target_lang": "es",
            "domain": "medical",
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["applied_glossary_terms"] == ["dosis"]


def test_translate_omits_forced_terms_for_auto_detect(client, promote_actor_to_admin):
    admin_token = promote_actor_to_admin("glossary-admin5@example.com")
    client.post(
        "/api/v1/glossary/",
        json={
            "domain": "medical",
            "source_lang": "en",
            "target_lang": "es",
            "source_term": "dosage",
            "target_term": "dosis",
        },
        headers=auth_headers(admin_token),
    )

    user_token = register_and_login(client, "glossary-user2@example.com")
    resp = client.post(
        "/api/v1/translate/",
        json={
            "text": "Confirm the dosage before dispensing.",
            "target_lang": "es",
            "domain": "medical",
        },
        headers=auth_headers(user_token),
    )
    assert resp.status_code == 200
    assert resp.json()["applied_glossary_terms"] == []
