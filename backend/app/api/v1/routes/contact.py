from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....core.config import settings
from ....core.limiter import limiter
from ....deps import get_db
from ....email_client import EmailClient, get_email_client
from ....models import ContactMessage

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post(
    "/",
    response_model=schemas.ContactMessageRead,
    summary="Submit the public Contact page form",
)
@limiter.limit("5/minute")
async def submit_contact_message(
    request: Request,
    body: schemas.ContactMessageCreate,
    db: AsyncSession = Depends(get_db),
    email_client: EmailClient = Depends(get_email_client),
):
    message = ContactMessage(
        name=body.name,
        email=body.email,
        subject=body.subject,
        message=body.message,
    )
    db.add(message)
    await db.commit()

    # Degrades to a log line if SMTP isn't configured, same as every other
    # email in this app — the message is still durably stored above either way.
    notify_address = settings.first_admin_email or settings.smtp_from_address
    email_client.send(
        notify_address,
        f"[Contact] {body.subject}",
        f"From: {body.name} <{body.email}>\n\n{body.message}",
    )
    return message
