from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....deps import get_db, require_any_role
from ....models import Correction, Translation

router = APIRouter(prefix="/review", tags=["review"])

REVIEWER_ROLES = ("translator", "admin")


@router.get(
    "/queue",
    response_model=list[schemas.TranslationRead],
    summary="Active-learning review queue: low-confidence translations awaiting a correction",
)
async def review_queue(
    min_confidence: float = 0.6,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _reviewer=Depends(require_any_role(*REVIEWER_ROLES)),
):
    limit = max(1, min(limit, 200))
    already_corrected = select(Correction.translation_id).distinct()
    result = await db.execute(
        select(Translation)
        .where(Translation.confidence < min_confidence)
        .where(~Translation.id.in_(already_corrected))
        .order_by(Translation.confidence.asc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post(
    "/{translation_id}/correct",
    response_model=schemas.CorrectionRead,
    summary="Submit a corrected translation (translator/admin only)",
)
async def submit_correction(
    translation_id: int,
    correction_in: schemas.CorrectionCreate,
    db: AsyncSession = Depends(get_db),
    reviewer=Depends(require_any_role(*REVIEWER_ROLES)),
):
    result = await db.execute(select(Translation).where(Translation.id == translation_id))
    translation = result.scalar_one_or_none()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    correction = Correction(
        translation_id=translation.id,
        reviewer_id=reviewer.id,
        corrected_text=correction_in.corrected_text,
        note=correction_in.note,
    )
    db.add(correction)
    await db.commit()
    return correction
