from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .... import schemas
from ....deps import get_current_active_user, get_db
from ....models import Feedback, Translation

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=schemas.AnalyticsSummary,
    summary="Personal translation analytics for the current user",
)
def analytics_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    # Aggregated in Python rather than with DB-side date-truncation SQL: SQLite
    # and Postgres don't share a portable CAST(... AS DATE)/date-trunc syntax
    # via SQLAlchemy's generic layer, and at the scale of one user's translation
    # history this is simple, correct, and fast enough. Revisit with DB-side
    # aggregation if this ever needs to summarize translations across all users.
    translations = db.query(Translation).filter(Translation.user_id == user.id).all()
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
            db.query(Feedback.rating)
            .filter(Feedback.translation_id.in_(translation_ids))
            .all()
        )
        rating_counts = Counter(rating for (rating,) in rating_rows)
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
