def test_submit_contact_message(client):
    resp = client.post(
        "/api/v1/contact/",
        json={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "subject": "Question about the API",
            "message": "Does the batch endpoint support more than 50 items?",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Ada Lovelace"
    assert body["subject"] == "Question about the API"
    assert "id" in body


def test_submit_contact_message_requires_fields(client):
    resp = client.post(
        "/api/v1/contact/",
        json={"name": "", "email": "not-an-email", "subject": "", "message": ""},
    )
    assert resp.status_code == 422


def test_contact_message_is_rate_limited(client):
    payload = {
        "name": "Repeat Sender",
        "email": "repeat@example.com",
        "subject": "Hi",
        "message": "Hello there",
    }
    for _ in range(5):
        resp = client.post("/api/v1/contact/", json=payload)
        assert resp.status_code == 200

    blocked = client.post("/api/v1/contact/", json=payload)
    assert blocked.status_code == 429
