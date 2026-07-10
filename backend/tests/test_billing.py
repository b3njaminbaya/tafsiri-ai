import json

from sqlalchemy import select

from app.models import APIKey

from .conftest import _fake_stripe, run_db
from .helpers import auth_headers, register_and_login


def _set_price_map(monkeypatch, mapping: str):
    import app.core.config as config_module

    monkeypatch.setattr(config_module.settings, "stripe_price_quota_map", mapping)


def test_list_plans(client, monkeypatch):
    _set_price_map(monkeypatch, "price_basic:1000,price_pro:100000")
    resp = client.get("/api/v1/billing/plans")
    assert resp.status_code == 200
    plans = {p["price_id"]: p["quota_limit"] for p in resp.json()}
    assert plans == {"price_basic": 1000, "price_pro": 100000}


def test_create_checkout_session(client, monkeypatch):
    _set_price_map(monkeypatch, "price_basic:1000")
    token = register_and_login(client, "billing_user@example.com")
    resp = client.post(
        "/api/v1/billing/checkout-session",
        json={"price_id": "price_basic"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["checkout_url"] == "https://fake-stripe.local/checkout/price_basic"


def test_create_checkout_session_requires_auth(client, monkeypatch):
    _set_price_map(monkeypatch, "price_basic:1000")
    resp = client.post("/api/v1/billing/checkout-session", json={"price_id": "price_basic"})
    assert resp.status_code == 401


def test_create_checkout_session_rejects_unknown_price(client, monkeypatch):
    _set_price_map(monkeypatch, "price_basic:1000")
    token = register_and_login(client, "billing_user2@example.com")
    resp = client.post(
        "/api/v1/billing/checkout-session",
        json={"price_id": "not-a-real-price"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 400


def test_webhook_updates_api_key_quota_on_checkout_completed(client, monkeypatch):
    _set_price_map(monkeypatch, "price_pro:100000")
    token = register_and_login(client, "webhook_user@example.com")
    created = client.post("/api/v1/auth/api-keys", headers=auth_headers(token))
    key_id = created.json()["api_key"]["id"]

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer_email": "webhook_user@example.com",
                "metadata": {"price_id": "price_pro"},
            }
        },
    }
    resp = client.post(
        "/api/v1/billing/webhook",
        content=json.dumps(event),
        headers={"stripe-signature": "valid-test-signature"},
    )
    assert resp.status_code == 200

    async def _check(db):
        result = await db.execute(select(APIKey).where(APIKey.id == key_id))
        return result.scalar_one()

    updated_key = run_db(_check)
    assert updated_key.quota_limit == 100000


def test_webhook_rejects_invalid_signature(client):
    resp = client.post(
        "/api/v1/billing/webhook",
        content=json.dumps({"type": "checkout.session.completed", "data": {"object": {}}}),
        headers={"stripe-signature": "wrong-signature"},
    )
    assert resp.status_code == 400


def test_checkout_session_returns_503_when_stripe_unconfigured(client, monkeypatch):
    _set_price_map(monkeypatch, "price_basic:1000")
    token = register_and_login(client, "billing_unconfigured@example.com")
    _fake_stripe.configured = False
    try:
        resp = client.post(
            "/api/v1/billing/checkout-session",
            json={"price_id": "price_basic"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 503
    finally:
        _fake_stripe.configured = True


def test_webhook_returns_503_when_unconfigured(client):
    _fake_stripe.webhook_configured = False
    try:
        resp = client.post(
            "/api/v1/billing/webhook",
            content=json.dumps({"type": "checkout.session.completed", "data": {"object": {}}}),
            headers={"stripe-signature": "valid-test-signature"},
        )
        assert resp.status_code == 503
    finally:
        _fake_stripe.webhook_configured = True


def test_webhook_ignores_unrelated_event_types(client, monkeypatch):
    _set_price_map(monkeypatch, "price_pro:100000")
    resp = client.post(
        "/api/v1/billing/webhook",
        content=json.dumps({"type": "customer.created", "data": {"object": {}}}),
        headers={"stripe-signature": "valid-test-signature"},
    )
    assert resp.status_code == 200
