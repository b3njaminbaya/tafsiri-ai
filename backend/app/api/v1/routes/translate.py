from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....cache import CacheClient, get_cache_client
from ....deps import get_current_user_or_api_key, get_db
from ....glossary import resolve_forced_terms
from ....ml_client import MLServiceClient, MLServiceError, get_ml_client
from ....models import Feedback, Translation

router = APIRouter(prefix="/translate", tags=["translation"])


@router.post(
    "/",
    response_model=schemas.TranslateResponse,
    summary="Translate text via ml-service. Accepts a JWT bearer token or an X-API-Key header.",
)
async def translate(
    req: schemas.TranslateRequest,
    user=Depends(get_current_user_or_api_key),
    db: AsyncSession = Depends(get_db),
    ml_client: MLServiceClient = Depends(get_ml_client),
    cache: CacheClient = Depends(get_cache_client),
):
    # Identical (text, source_lang, target_lang, domain) requests are common
    # in real translation traffic (the same UI string, the same FAQ entry,
    # the same product description) — short-circuit the ml-service call
    # rather than re-running inference for an answer already computed. Still
    # persisted as a normal Translation row below: caching the model call is
    # an implementation detail, not something that should hide a user's own
    # history of what they translated and when.
    cache_key = CacheClient.translation_key(req.text, req.source_lang, req.target_lang, req.domain)
    result = cache.get(cache_key)
    cache_hit = result is not None

    if result is None:
        forced_terms = await resolve_forced_terms(
            db, req.domain, req.source_lang, req.target_lang, req.text
        )
        try:
            result = await ml_client.translate(
                req.text, req.target_lang, req.source_lang, req.domain, forced_terms
            )
        except MLServiceError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc
        cache.set(cache_key, result)

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
    await db.commit()

    return schemas.TranslateResponse(
        id=record.id,
        translation=record.output_text,
        source_lang=record.source_lang,
        target_lang=record.target_lang,
        domain=record.domain,
        confidence=record.confidence,
        applied_glossary_terms=result.get("applied_glossary_terms", []),
        cached=cache_hit,
    )


@router.post(
    "/batch",
    response_model=schemas.BatchTranslateResponse,
    summary="Translate up to 50 texts in one call — real batched inference where possible.",
)
async def translate_batch(
    req: schemas.BatchTranslateRequest,
    user=Depends(get_current_user_or_api_key),
    db: AsyncSession = Depends(get_db),
    ml_client: MLServiceClient = Depends(get_ml_client),
):
    try:
        batch_items = []
        for item in req.items:
            forced_terms = await resolve_forced_terms(
                db, item.domain, item.source_lang, item.target_lang, item.text
            )
            batch_items.append(
                {
                    "text": item.text,
                    "target_lang": item.target_lang,
                    "source_lang": item.source_lang,
                    "domain": item.domain,
                    "forced_terms": forced_terms,
                }
            )
        raw_results = await ml_client.translate_batch(batch_items)
    except MLServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    responses = []
    for item, result in zip(req.items, raw_results):
        record = Translation(
            user_id=user.id,
            source_lang=result.get("source_lang"),
            target_lang=item.target_lang,
            domain=item.domain,
            input_text=item.text,
            output_text=result["translation"],
            confidence=result["confidence"],
        )
        db.add(record)
        await db.flush()
        responses.append(
            schemas.TranslateResponse(
                id=record.id,
                translation=record.output_text,
                source_lang=record.source_lang,
                target_lang=record.target_lang,
                domain=record.domain,
                confidence=record.confidence,
                applied_glossary_terms=result.get("applied_glossary_terms", []),
            )
        )
    await db.commit()
    return schemas.BatchTranslateResponse(results=responses)


@router.get(
    "/history",
    response_model=list[schemas.TranslationRead],
    summary="List the current user's past translations, most recent first",
)
async def translation_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_or_api_key),
):
    limit = max(1, min(limit, 200))
    result = await db.execute(
        select(Translation)
        .where(Translation.user_id == user.id)
        .order_by(Translation.id.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post(
    "/{translation_id}/feedback",
    response_model=schemas.FeedbackRead,
    summary="Rate one of your own past translations",
)
async def submit_feedback(
    translation_id: int,
    feedback_in: schemas.FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user_or_api_key),
):
    result = await db.execute(
        select(Translation).where(
            Translation.id == translation_id, Translation.user_id == user.id
        )
    )
    translation = result.scalar_one_or_none()
    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    feedback = Feedback(
        user_id=user.id,
        translation_id=translation.id,
        rating=feedback_in.rating,
        comment=feedback_in.comment,
    )
    db.add(feedback)
    await db.commit()
    return feedback
