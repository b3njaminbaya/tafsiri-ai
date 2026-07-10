from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....core.config import settings
from ....deps import get_current_active_user, get_db
from ....models import Dataset
from ....storage import get_s3_client, get_s3_public_client

router = APIRouter(prefix="/datasets", tags=["datasets"])

PRESIGNED_URL_TTL_SECONDS = 3600

# Parallel-corpus dataset formats we know how to eventually parse for
# training. Anything else (executables, archives, images, ...) is rejected
# up front rather than silently stored and failing later at training time.
ALLOWED_DATASET_EXTENSIONS = {".tsv", ".csv", ".txt", ".json", ".jsonl", ".tmx", ".xliff", ".xlf"}


def _validate_dataset_filename(filename: str | None) -> None:
    if not filename or "." not in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset file must have one of these extensions: "
            + ", ".join(sorted(ALLOWED_DATASET_EXTENSIONS)),
        )
    extension = "." + filename.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_DATASET_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{extension}'. Allowed: "
            + ", ".join(sorted(ALLOWED_DATASET_EXTENSIONS)),
        )


@router.get("/", response_model=list[schemas.DatasetRead], summary="List available datasets")
async def list_datasets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dataset).order_by(Dataset.id.desc()))
    return result.scalars().all()


@router.post(
    "/",
    response_model=schemas.DatasetRead,
    summary="Upload a parallel-corpus dataset file",
)
async def upload_dataset(
    name: str = Form(...),
    description: str = Form(None),
    source_lang: str = Form(None),
    target_lang: str = Form(None),
    domain: str = Form(None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
    s3_client=Depends(get_s3_client),
):
    _validate_dataset_filename(file.filename)

    content = await file.read(settings.max_dataset_upload_bytes + 1)
    if len(content) > settings.max_dataset_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Dataset file exceeds the {settings.max_dataset_upload_bytes} byte limit",
        )
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    storage_key = f"{uuid4()}-{file.filename}"
    s3_client.put_object(
        Bucket=settings.minio_bucket_datasets,
        Key=storage_key,
        Body=content,
    )

    dataset = Dataset(
        name=name,
        description=description,
        source_lang=source_lang,
        target_lang=target_lang,
        domain=domain,
        storage_key=storage_key,
        size_bytes=len(content),
        uploaded_by_id=user.id,
    )
    db.add(dataset)
    await db.commit()
    return dataset


@router.get(
    "/{dataset_id}/download",
    response_model=schemas.DatasetDownloadResponse,
    summary="Get a time-limited download URL for a dataset",
)
async def download_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    s3_public_client=Depends(get_s3_public_client),
):
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    url = s3_public_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.minio_bucket_datasets, "Key": dataset.storage_key},
        ExpiresIn=PRESIGNED_URL_TTL_SECONDS,
    )
    return schemas.DatasetDownloadResponse(url=url, expires_in_seconds=PRESIGNED_URL_TTL_SECONDS)
