from datetime import datetime, timezone
from secrets import token_urlsafe

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....deps import get_current_active_user, get_db
from ....models import APIKey, Correction, Dataset, Feedback, GdprRequest, PrivacySettings, Translation, User

router = APIRouter(prefix="/privacy", tags=["privacy"])


async def _get_or_create_settings(db: AsyncSession, user_id: int) -> PrivacySettings:
    result = await db.execute(select(PrivacySettings).where(PrivacySettings.user_id == user_id))
    row = result.scalar_one_or_none()
    if not row:
        row = PrivacySettings(user_id=user_id)
        db.add(row)
        await db.commit()
    return row


@router.get(
    "/settings",
    response_model=schemas.PrivacySettingsRead,
    summary="Your saved privacy/consent preferences",
)
async def get_privacy_settings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return await _get_or_create_settings(db, user.id)


@router.put(
    "/settings",
    response_model=schemas.PrivacySettingsRead,
    summary="Update your privacy/consent preferences",
)
async def update_privacy_settings(
    body: schemas.PrivacySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    row = await _get_or_create_settings(db, user.id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    await db.commit()
    return row


@router.get(
    "/export",
    response_model=schemas.DataExport,
    summary="Download all of your own data — a real, immediate export, not an emailed promise",
)
async def export_data(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    translations = (
        (await db.execute(select(Translation).where(Translation.user_id == user.id))).scalars().all()
    )
    feedback = (
        (await db.execute(select(Feedback).where(Feedback.user_id == user.id))).scalars().all()
    )
    corrections = (
        (await db.execute(select(Correction).where(Correction.reviewer_id == user.id))).scalars().all()
    )
    datasets = (
        (await db.execute(select(Dataset).where(Dataset.uploaded_by_id == user.id))).scalars().all()
    )
    api_keys = (
        (await db.execute(select(APIKey).where(APIKey.user_id == user.id))).scalars().all()
    )

    return schemas.DataExport(
        user=user,
        translations=translations,
        feedback_given=feedback,
        corrections_given=corrections,
        datasets_uploaded=datasets,
        api_keys=api_keys,
    )


@router.post(
    "/delete-account",
    summary="Anonymize your account and revoke your API keys",
)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    # Anonymize rather than hard-delete: translations/corrections/dataset
    # uploads are real content other parts of the system (community stats,
    # the review queue, other users' downloads) legitimately still reference.
    # GDPR erasure doesn't require destroying data once it's anonymized.
    user.email = f"deleted-user-{user.id}-{token_urlsafe(8)}@deleted.local"
    user.hashed_password = None
    user.is_active = False
    user.oauth_provider = None
    user.oauth_subject = None

    keys = (await db.execute(select(APIKey).where(APIKey.user_id == user.id))).scalars().all()
    for key in keys:
        key.is_active = False

    await db.commit()
    return {"message": "Account anonymized and deactivated"}


@router.post(
    "/gdpr-requests",
    response_model=schemas.GdprRequestRead,
    summary="Submit a data-rights request",
)
async def submit_gdpr_request(
    body: schemas.GdprRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    # access/portability are fully served by GET /privacy/export already, so
    # they're logged as completed immediately; rectification/restrict/object
    # need a human and stay pending — there's no admin review UI for those
    # yet (see docs/AUDIT.md), but the request is now genuinely recorded
    # instead of vanishing into a fake "we'll respond in 30 days" toast.
    auto_completed = body.request_type in ("access", "portability")
    request_row = GdprRequest(
        user_id=user.id,
        request_type=body.request_type,
        description=body.description,
        status="completed" if auto_completed else "pending",
        resolved_at=datetime.now(timezone.utc) if auto_completed else None,
    )
    db.add(request_row)
    await db.commit()
    return request_row


@router.get(
    "/gdpr-requests",
    response_model=list[schemas.GdprRequestRead],
    summary="List your own submitted data-rights requests",
)
async def list_gdpr_requests(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(GdprRequest).where(GdprRequest.user_id == user.id).order_by(GdprRequest.id.desc())
    )
    return result.scalars().all()
