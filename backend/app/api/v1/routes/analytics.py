from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....deps import get_current_active_user, get_db, require_role
from ....models import Dataset, Feedback, Translation, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


async def _summarize(db: AsyncSession, user_id: Optional[int]) -> schemas.AnalyticsSummary:
    """Aggregated entirely in SQL (GROUP BY/COUNT/AVG), not by loading every
    matching Translation row into Python — the old approach did `select(...)`
    with no limit and iterated in memory, which for /analytics/global means
    every translation ever made on the platform, on every request.
    func.date(...) (not CAST(... AS DATE)) is used for the day bucket: it
    renders as SQLite's and Postgres's own `date()` function on each backend
    respectively, and — critically — is never asked to deserialize back into
    a Python date via SQLAlchemy's generic DateTime type, which is what
    caused the `TypeError: fromisoformat: argument must be str` this project
    hit previously when this was written as a CAST. We just format the
    already-stringy label directly, on both databases.
    """
    translation_filter = () if user_id is None else (Translation.user_id == user_id,)

    total, average_confidence = (
        await db.execute(
            select(
                func.count(Translation.id),
                func.coalesce(func.avg(Translation.confidence), 0.0),
            ).where(*translation_filter)
        )
    ).one()

    day_expr = func.date(Translation.created_at)
    daily_rows = (
        await db.execute(
            select(day_expr, func.count())
            .where(*translation_filter)
            .group_by(day_expr)
            .order_by(day_expr)
        )
    ).all()
    translations_by_day = [
        schemas.DailyCount(date=str(day), count=count) for day, count in daily_rows if day is not None
    ]

    pair_rows = (
        await db.execute(
            select(Translation.source_lang, Translation.target_lang, func.count().label("cnt"))
            .where(*translation_filter)
            .group_by(Translation.source_lang, Translation.target_lang)
            .order_by(func.count().desc())
            .limit(10)
        )
    ).all()
    top_language_pairs = [
        schemas.LanguagePairCount(source_lang=s, target_lang=t, count=c) for s, t, c in pair_rows
    ]

    feedback_query = select(Feedback.rating, func.count()).group_by(Feedback.rating)
    if user_id is not None:
        feedback_query = feedback_query.join(
            Translation, Translation.id == Feedback.translation_id
        ).where(Translation.user_id == user_id)
    feedback_rows = (await db.execute(feedback_query.order_by(Feedback.rating))).all()
    feedback_breakdown = [schemas.RatingBreakdown(rating=r, count=c) for r, c in feedback_rows]

    return schemas.AnalyticsSummary(
        total_translations=total,
        average_confidence=float(average_confidence),
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
    return await _summarize(db, user.id)


@router.get(
    "/global",
    response_model=schemas.GlobalAnalyticsSummary,
    summary="Platform-wide translation analytics (admin only)",
)
async def global_analytics_summary(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    summary = await _summarize(db, None)
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_datasets = (await db.execute(select(func.count(Dataset.id)))).scalar_one()
    return schemas.GlobalAnalyticsSummary(
        **summary.model_dump(),
        total_users=total_users,
        total_datasets=total_datasets,
    )
