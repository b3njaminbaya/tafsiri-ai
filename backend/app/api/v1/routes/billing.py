from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....billing_client import BillingError, StripeClient, get_stripe_client
from ....core.config import settings
from ....deps import get_current_active_user, get_db
from ....email_client import EmailClient, get_email_client
from ....models import APIKey, User
from ....security import hash_api_key, normalize_email

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get(
    "/plans",
    response_model=list[schemas.PlanRead],
    summary="Available subscription plans and the API quota each grants",
)
def list_plans():
    return [
        schemas.PlanRead(price_id=price_id, quota_limit=quota)
        for price_id, quota in settings.stripe_price_to_quota.items()
    ]


@router.post(
    "/checkout-session",
    response_model=schemas.CheckoutSessionResponse,
    summary="Create a Stripe Checkout session for a subscription plan",
)
async def create_checkout_session(
    req: schemas.CheckoutSessionRequest,
    user: User = Depends(get_current_active_user),
    stripe_client: StripeClient = Depends(get_stripe_client),
):
    if req.price_id not in settings.stripe_price_to_quota:
        raise HTTPException(status_code=400, detail="Unknown price_id")
    if not stripe_client.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing is not configured on this server",
        )
    try:
        checkout_url = stripe_client.create_checkout_session(
            req.price_id,
            user.email,
            settings.stripe_checkout_success_url,
            settings.stripe_checkout_cancel_url,
        )
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return schemas.CheckoutSessionResponse(checkout_url=checkout_url)


@router.post(
    "/webhook",
    summary="Stripe webhook — raises the caller's API key quota on a completed checkout",
)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_client: StripeClient = Depends(get_stripe_client),
    email_client: EmailClient = Depends(get_email_client),
):
    if not stripe_client.webhook_is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook is not configured on this server",
        )
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = stripe_client.construct_webhook_event(payload, sig_header)
    except BillingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if event.get("type") == "checkout.session.completed":
        session_obj = event["data"]["object"]
        customer_email = session_obj.get("customer_email") or (
            session_obj.get("customer_details") or {}
        ).get("email")
        price_id = (session_obj.get("metadata") or {}).get("price_id")
        quota_limit = settings.stripe_price_to_quota.get(price_id)

        if customer_email and quota_limit is not None:
            user = (
                await db.execute(
                    select(User).where(User.email == normalize_email(customer_email))
                )
            ).scalar_one_or_none()
            if user:
                # The plan a customer just paid for is one entitlement for
                # their account, not "give every key they happen to own the
                # full new quota" (the old behavior, which let a user with N
                # keys multiply one purchase into N times the quota). Apply
                # it to a single key: their most-recently-created active one.
                existing_keys = (
                    (
                        await db.execute(
                            select(APIKey)
                            .where(APIKey.user_id == user.id, APIKey.is_active.is_(True))
                            .order_by(APIKey.created_at.desc(), APIKey.id.desc())
                        )
                    )
                    .scalars()
                    .all()
                )
                if existing_keys:
                    existing_keys[0].quota_limit = quota_limit
                else:
                    # A customer can subscribe before ever creating an API
                    # key — the old code silently granted nothing in that
                    # case (payment succeeded, entitlement vanished). Mint
                    # one now and email the raw secret, since a webhook has
                    # no user-facing response to return it in.
                    raw_key = token_urlsafe(32)
                    new_key = APIKey(
                        hashed_key=hash_api_key(raw_key),
                        key_prefix=raw_key[:10],
                        user_id=user.id,
                        quota_limit=quota_limit,
                        is_active=True,
                    )
                    db.add(new_key)
                    email_client.send(
                        user.email,
                        "Your Tafsiri AI API key",
                        "Thanks for subscribing! Here is your new API key:\n\n"
                        f"{raw_key}\n\n"
                        "Keep it secret — it will not be shown again. You can "
                        "revoke it and create new ones from your account at any time.",
                    )
                await db.commit()

    return {"received": True}
