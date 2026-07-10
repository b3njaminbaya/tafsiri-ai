from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
def review_queue(
    min_confidence: float = 0.6,
    limit: int = 50,
    db: Session = Depends(get_db),
    _reviewer=Depends(require_any_role(*REVIEWER_ROLES)),
):
    limit = max(1, min(limit, 200))
    already_corrected = db.query(Correction.translation_id).distinct()
    return (
        db.query(Translation)
        .filter(Translation.confidence < min_confidence)
        .filter(~Translation.id.in_(already_corrected))
        .order_by(Translation.confidence.asc())
        .limit(limit)
        .all()
    )


@router.post(
    "/{translation_id}/correct",
    response_model=schemas.CorrectionRead,
    summary="Submit a corrected translation (translator/admin only)",
)
def submit_correction(
    translation_id: int,
    correction_in: schemas.CorrectionCreate,
    db: Session = Depends(get_db),
    reviewer=Depends(require_any_role(*REVIEWER_ROLES)),
):
    translation = db.query(Translation).filter(Translation.id == translation_id).first()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    correction = Correction(
        translation_id=translation.id,
        reviewer_id=reviewer.id,
        corrected_text=correction_in.corrected_text,
        note=correction_in.note,
    )
    db.add(correction)
    db.commit()
    db.refresh(correction)
    return correction
