from fastapi import APIRouter, Depends
from .... import schemas
from ....deps import get_current_user_or_api_key

router = APIRouter(prefix="/translate", tags=["translation"])

@router.post(
    "/",
    response_model=schemas.TranslateResponse,
    summary="Translate text (placeholder). Accepts a JWT bearer token or an X-API-Key header.",
)
def translate(req: schemas.TranslateRequest, user=Depends(get_current_user_or_api_key)):
    # Placeholder: echo back text with simple mock transformation
    translated = f"[{req.target_lang}] " + req.text[::-1]
    confidence = 0.42
    detected = req.source_lang or "auto"
    return schemas.TranslateResponse(
        translation=translated,
        source_lang=detected,
        target_lang=req.target_lang,
        domain=req.domain,
        confidence=confidence,
    )
