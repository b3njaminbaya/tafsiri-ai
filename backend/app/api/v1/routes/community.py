from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from .... import schemas
from ....deps import get_db
from ....models import Correction, Dataset, Translation, User

router = APIRouter(prefix="/community", tags=["community"])


def _handle(email: str) -> str:
    """Local-part of the email only — enough for public attribution/recognition
    without exposing a full email address (including provider domain) on an
    unauthenticated endpoint. A dedicated display-name field would be the
    proper long-term fix; this is the responsible interim choice.
    """
    return email.split("@")[0]


@router.get(
    "/stats",
    response_model=schemas.CommunityStats,
    summary="Public community contribution stats (datasets, translations, reviews)",
)
def community_stats(db: Session = Depends(get_db)):
    total_datasets = db.query(Dataset).count()
    total_translations = db.query(Translation).count()
    total_corrections = db.query(Correction).count()

    contributor_ids = set()
    contributor_ids.update(uid for (uid,) in db.query(Dataset.uploaded_by_id).distinct())
    contributor_ids.update(uid for (uid,) in db.query(Correction.reviewer_id).distinct())

    top_dataset_contributors = (
        db.query(User.email, func.count(Dataset.id).label("count"))
        .join(Dataset, Dataset.uploaded_by_id == User.id)
        .group_by(User.email)
        .order_by(func.count(Dataset.id).desc())
        .limit(5)
        .all()
    )
    top_reviewers = (
        db.query(User.email, func.count(Correction.id).label("count"))
        .join(Correction, Correction.reviewer_id == User.id)
        .group_by(User.email)
        .order_by(func.count(Correction.id).desc())
        .limit(5)
        .all()
    )

    return schemas.CommunityStats(
        total_datasets=total_datasets,
        total_translations=total_translations,
        total_corrections=total_corrections,
        total_contributors=len(contributor_ids),
        top_dataset_contributors=[
            schemas.ContributorCount(handle=_handle(email), count=count)
            for email, count in top_dataset_contributors
        ],
        top_reviewers=[
            schemas.ContributorCount(handle=_handle(email), count=count)
            for email, count in top_reviewers
        ],
    )
