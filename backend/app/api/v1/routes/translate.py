from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .... import schemas
from ....deps import get_current_user_or_api_key, get_db
from ....ml_client import MLServiceClient, MLServiceError, get_ml_client
from ....models import Feedback, Translation

router = APIRouter(prefix="/translate", tags=["translation"])


@router.post(
    "/",
    response_model=schemas.TranslateResponse,
    summary="Translate text via ml-service. Accepts a JWT bearer token or an X-API-Key header.",
)
def translate(
    req: schemas.TranslateRequest,
    user=Depends(get_current_user_or_api_key),
    db: Session = Depends(get_db),
    ml_client: MLServiceClient = Depends(get_ml_client),
):
    try:
        result = ml_client.translate(
            req.text, req.target_lang, req.source_lang, req.domain
        )
    except MLServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    record = Translation(
        user_id=user.id,
        source_lang=result.get("source_lang"),
        target_lang=req.target_lang,
        domain=req.domain,
        input_text=req.text,
        output_text=result["translation"],
        confidence=result["confidence"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return schemas.TranslateResponse(
        id=record.id,
        translation=record.output_text,
        source_lang=record.source_lang,
        target_lang=record.target_lang,
        domain=record.domain,
        confidence=record.confidence,
    )


@router.get(
    "/history",
    response_model=list[schemas.TranslationRead],
    summary="List the current user's past translations, most recent first",
)
def translation_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_or_api_key),
):
    limit = max(1, min(limit, 200))
    return (
        db.query(Translation)
        .filter(Translation.user_id == user.id)
        .order_by(Translation.id.desc())
        .limit(limit)
        .all()
    )


@router.post(
    "/{translation_id}/feedback",
    response_model=schemas.FeedbackRead,
    summary="Rate one of your own past translations",
)
def submit_feedback(
    translation_id: int,
    feedback_in: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_or_api_key),
):
    translation = (
        db.query(Translation)
        .filter(Translation.id == translation_id, Translation.user_id == user.id)
        .first()
    )
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    feedback = Feedback(
        user_id=user.id,
        translation_id=translation.id,
        rating=feedback_in.rating,
        comment=feedback_in.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
