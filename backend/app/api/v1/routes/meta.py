from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....cache import CacheClient, get_cache_client
from ....core.config import settings
from ....deps import get_db
from ....ml_client import MLServiceClient, MLServiceError, get_ml_client
from ....storage import get_s3_client

router = APIRouter(tags=["meta"])


@router.get("/languages", summary="Supported languages (proxied from ml-service)")
async def languages(ml_client: MLServiceClient = Depends(get_ml_client)):
    try:
        return await ml_client.get_languages()
    except MLServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get(
    "/languages/roadmap",
    summary="Kenyan languages not yet supported (no pretrained model coverage)",
)
async def languages_roadmap(ml_client: MLServiceClient = Depends(get_ml_client)):
    try:
        return await ml_client.get_languages_roadmap()
    except MLServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get(
    "/status",
    response_model=schemas.SystemStatus,
    summary="Real, live health of every backend dependency (DB, cache, storage, ml-service)",
)
async def system_status(
    db: AsyncSession = Depends(get_db),
    cache: CacheClient = Depends(get_cache_client),
    s3_client=Depends(get_s3_client),
    ml_client: MLServiceClient = Depends(get_ml_client),
):
    """Backs the frontend SystemStatus page, which previously showed
    hardcoded "operational" text, fake uptime percentages, and fake incident
    timestamps while claiming to be "real-time". This actually checks each
    dependency on every call rather than reporting a fixed fiction.
    """
    dependencies: dict[str, schemas.DependencyStatus] = {}

    try:
        await db.execute(select(1))
        dependencies["database"] = schemas.DependencyStatus(status="operational")
    except Exception as exc:
        dependencies["database"] = schemas.DependencyStatus(status="down", detail=str(exc))

    if cache.ping():
        dependencies["cache"] = schemas.DependencyStatus(status="operational")
    else:
        dependencies["cache"] = schemas.DependencyStatus(status="down", detail="Redis unreachable")

    try:
        # head_bucket (scoped to the one configured bucket), not
        # list_buckets (account-wide) — a storage credential scoped to a
        # single bucket, the least-privilege setup this project actually
        # uses in production (see infra docs), legitimately can't call
        # ListBuckets at all. Verified live: a bucket-scoped R2 token gets
        # AccessDenied from list_buckets() but works fine here.
        s3_client.head_bucket(Bucket=settings.minio_bucket_datasets)
        dependencies["storage"] = schemas.DependencyStatus(status="operational")
    except Exception as exc:
        dependencies["storage"] = schemas.DependencyStatus(status="down", detail=str(exc))

    try:
        health = await ml_client.get_health()
        ml_status = "operational" if health.get("model_loaded") else "degraded"
        dependencies["translation_model"] = schemas.DependencyStatus(status=ml_status)
    except MLServiceError as exc:
        dependencies["translation_model"] = schemas.DependencyStatus(status="down", detail=str(exc))

    statuses = {d.status for d in dependencies.values()}
    if statuses == {"operational"}:
        overall = "operational"
    elif "down" in statuses:
        overall = "down" if statuses == {"down"} else "degraded"
    else:
        overall = "degraded"

    return schemas.SystemStatus(
        status=overall,
        checked_at=datetime.now(timezone.utc),
        dependencies=dependencies,
    )


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
