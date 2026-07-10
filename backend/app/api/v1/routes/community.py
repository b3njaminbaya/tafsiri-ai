from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from .... import schemas
from ....deps import get_db
from ....handles import public_handle
from ....models import Correction, Dataset, Translation, User

router = APIRouter(prefix="/community", tags=["community"])


@router.get(
    "/stats",
    response_model=schemas.CommunityStats,
    summary="Public community contribution stats (datasets, translations, reviews)",
)
async def community_stats(db: AsyncSession = Depends(get_db)):
    total_datasets = (await db.execute(select(func.count(Dataset.id)))).scalar_one()
    total_translations = (await db.execute(select(func.count(Translation.id)))).scalar_one()
    total_corrections = (await db.execute(select(func.count(Correction.id)))).scalar_one()

    dataset_uploader_ids = (
        (await db.execute(select(Dataset.uploaded_by_id).distinct())).scalars().all()
    )
    reviewer_ids = (
        (await db.execute(select(Correction.reviewer_id).distinct())).scalars().all()
    )
    contributor_ids = set(dataset_uploader_ids) | set(reviewer_ids)

    top_dataset_contributors = (
        await db.execute(
            select(User.display_name, User.email, func.count(Dataset.id).label("count"))
            .join(Dataset, Dataset.uploaded_by_id == User.id)
            .group_by(User.display_name, User.email)
            .order_by(func.count(Dataset.id).desc())
            .limit(5)
        )
    ).all()
    top_reviewers = (
        await db.execute(
            select(User.display_name, User.email, func.count(Correction.id).label("count"))
            .join(Correction, Correction.reviewer_id == User.id)
            .group_by(User.display_name, User.email)
            .order_by(func.count(Correction.id).desc())
            .limit(5)
        )
    ).all()

    return schemas.CommunityStats(
        total_datasets=total_datasets,
        total_translations=total_translations,
        total_corrections=total_corrections,
        total_contributors=len(contributor_ids),
        top_dataset_contributors=[
            schemas.ContributorCount(handle=public_handle(display_name, email), count=count)
            for display_name, email, count in top_dataset_contributors
        ],
        top_reviewers=[
            schemas.ContributorCount(handle=public_handle(display_name, email), count=count)
            for display_name, email, count in top_reviewers
        ],
    )
