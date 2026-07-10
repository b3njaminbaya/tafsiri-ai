import app.core.config as config_module


def test_first_admin_email_gets_admin_role(client, monkeypatch):
    monkeypatch.setattr(config_module.settings, "first_admin_email", "boss@example.com")
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "boss@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"]["name"] == "admin"


def test_first_admin_email_match_is_case_insensitive(client, monkeypatch):
    monkeypatch.setattr(config_module.settings, "first_admin_email", "CaseBoss@Example.com")
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "caseboss@example.com", "password": "secret123"},
    )
    assert resp.json()["role"]["name"] == "admin"


def test_other_emails_unaffected_by_first_admin_setting(client, monkeypatch):
    monkeypatch.setattr(config_module.settings, "first_admin_email", "boss@example.com")
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "notboss@example.com", "password": "secret123"},
    )
    assert resp.json()["role"]["name"] == "user"


def test_first_admin_email_unset_by_default(client):
    # No monkeypatch — default empty string means this never matches anyone,
    # so registration behaves exactly as it did before this setting existed.
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "anyone@example.com", "password": "secret123"},
    )
    assert resp.json()["role"]["name"] == "user"
