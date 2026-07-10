import stripe

from .core.config import settings


class BillingError(Exception):
    """Raised when Stripe is unreachable, misconfigured, or rejects a request."""


class StripeClient:
    """Thin wrapper around the Stripe SDK — dependency-injectable so tests use
    a fake instead of calling the real Stripe API. Note: this wrapper is
    tested against a fake client only; there are no Stripe test-mode
    credentials in this environment to verify it against the real API. Wire
    real STRIPE_SECRET_KEY/STRIPE_WEBHOOK_SECRET values and verify against a
    real Stripe test account before relying on this in production.
    """

    def __init__(self, secret_key: str, webhook_secret: str):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret

    @property
    def is_configured(self) -> bool:
        return bool(self.secret_key)

    @property
    def webhook_is_configured(self) -> bool:
        return bool(self.webhook_secret)

    def create_checkout_session(
        self, price_id: str, customer_email: str, success_url: str, cancel_url: str
    ) -> str:
        if not self.is_configured:
            raise BillingError("Stripe is not configured on this server (STRIPE_SECRET_KEY unset)")
        try:
            session = stripe.checkout.Session.create(
                api_key=self.secret_key,
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
                customer_email=customer_email,
                success_url=success_url,
                cancel_url=cancel_url,
                # Round-tripped back on the webhook event so the handler knows
                # which quota tier to apply without a follow-up API call.
                metadata={"price_id": price_id},
            )
        except stripe.error.StripeError as exc:
            raise BillingError(str(exc)) from exc
        return session.url

    def construct_webhook_event(self, payload: bytes, sig_header: str) -> dict:
        if not self.webhook_is_configured:
            raise BillingError("Stripe webhook is not configured on this server (STRIPE_WEBHOOK_SECRET unset)")
        try:
            return stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as exc:
            raise BillingError(f"Invalid webhook payload/signature: {exc}") from exc


def get_stripe_client() -> StripeClient:
    return StripeClient(settings.stripe_secret_key, settings.stripe_webhook_secret)
