from collections import Counter
from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....deps import get_current_active_user, get_db, require_role
from ....models import Dataset, Feedback, Translation, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def _summarize(db: AsyncSession, translations: Sequence[Translation]) -> schemas.AnalyticsSummary:
    # Aggregated in Python rather than with DB-side date-truncation SQL: SQLite
    # and Postgres don't share a portable CAST(... AS DATE)/date-trunc syntax
    # via SQLAlchemy's generic layer, and at the scale this runs at (one
    # user's history, or the whole platform's) this is simple, correct, and
    # fast enough. Revisit with DB-side aggregation if translation volume
    # grows large enough for this to matter.
    total = len(translations)
    average_confidence = (
        sum(t.confidence for t in translations) / total if total else 0.0
    )

    daily_counts = Counter(t.created_at.date().isoformat() for t in translations)
    translations_by_day = [
        schemas.DailyCount(date=day, count=count) for day, count in sorted(daily_counts.items())
    ]

    pair_counts = Counter((t.source_lang, t.target_lang) for t in translations)
    top_language_pairs = [
        schemas.LanguagePairCount(source_lang=s, target_lang=t, count=c)
        for (s, t), c in sorted(pair_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
    ]

    rating_counts: Counter = Counter()
    translation_ids = [t.id for t in translations]
    if translation_ids:
        rating_rows = (
            (
                await db.execute(
                    select(Feedback.rating).where(Feedback.translation_id.in_(translation_ids))
                )
            )
            .scalars()
            .all()
        )
        rating_counts = Counter(rating_rows)
    feedback_breakdown = [
        schemas.RatingBreakdown(rating=r, count=c) for r, c in sorted(rating_counts.items())
    ]

    return schemas.AnalyticsSummary(
        total_translations=total,
        average_confidence=average_confidence,
        translations_by_day=translations_by_day,
        top_language_pairs=top_language_pairs,
        feedback_breakdown=feedback_breakdown,
    )


@router.get(
    "/summary",
    response_model=schemas.AnalyticsSummary,
    summary="Personal translation analytics for the current user",
)
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_active_user),
):
    translations = (
        (await db.execute(select(Translation).where(Translation.user_id == user.id)))
        .scalars()
        .all()
    )
    return await _summarize(db, translations)


@router.get(
    "/global",
    response_model=schemas.GlobalAnalyticsSummary,
    summary="Platform-wide translation analytics (admin only)",
)
async def global_analytics_summary(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    translations = (await db.execute(select(Translation))).scalars().all()
    summary = await _summarize(db, translations)
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_datasets = (await db.execute(select(func.count(Dataset.id)))).scalar_one()
    return schemas.GlobalAnalyticsSummary(
        **summary.model_dump(),
        total_users=total_users,
        total_datasets=total_datasets,
    )
