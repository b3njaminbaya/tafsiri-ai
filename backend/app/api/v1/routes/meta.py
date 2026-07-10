from fastapi import APIRouter, Depends, HTTPException, status

from ....ml_client import MLServiceClient, MLServiceError, get_ml_client

router = APIRouter(tags=["meta"])


@router.get("/languages", summary="Supported languages (proxied from ml-service)")
async def languages(ml_client: MLServiceClient = Depends(get_ml_client)):
    try:
        return await ml_client.get_languages()
    except MLServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/models", summary="The translation model currently serving requests")
async def models(ml_client: MLServiceClient = Depends(get_ml_client)):
    try:
        health = await ml_client.get_health()
    except MLServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {
        "models": [
            {
                "name": health["model_name"],
                "type": "translation",
                "loaded": health["model_loaded"],
            }
        ]
    }
