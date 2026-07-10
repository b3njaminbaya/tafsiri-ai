import pytest

from app.billing_client import BillingError, StripeClient


def test_is_configured_reflects_secret_key():
    assert not StripeClient("", "").is_configured
    assert StripeClient("sk_test_123", "").is_configured


def test_webhook_is_configured_reflects_webhook_secret():
    assert not StripeClient("sk_test_123", "").webhook_is_configured
    assert StripeClient("sk_test_123", "whsec_123").webhook_is_configured


def test_create_checkout_session_fails_fast_when_unconfigured():
    client = StripeClient("", "")
    with pytest.raises(BillingError, match="not configured"):
        client.create_checkout_session("price_x", "a@example.com", "https://x", "https://y")


def test_construct_webhook_event_fails_fast_when_unconfigured():
    client = StripeClient("sk_test_123", "")
    with pytest.raises(BillingError, match="not configured"):
        client.construct_webhook_event(b"{}", "sig")
