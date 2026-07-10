import re
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import GlossaryTerm


async def resolve_forced_terms(
    db: AsyncSession,
    domain: Optional[str],
    source_lang: Optional[str],
    target_lang: str,
    text: str,
) -> Optional[List[str]]:
    """DB-backed replacement for ml-service's small hardcoded glossary dict —
    the backend now owns this data (admin-manageable via /glossary) and
    resolves matches itself, passing the result to ml-service's
    `forced_terms` override so it skips its own internal lookup.

    Returns None (not an empty list) when source_lang isn't known yet (the
    caller asked for auto-detection) — glossary matching needs the *actual*
    source language, which only ml-service's langdetect step can resolve for
    an auto-detect request. In that one case, forced_terms is left
    unset on the outgoing request so ml-service falls back to its own
    (smaller, static) internal glossary rather than getting no forcing at
    all — a deliberate, documented limitation, not a silent gap.
    """
    if not domain or not source_lang or source_lang == "auto":
        return None

    result = await db.execute(
        select(GlossaryTerm).where(
            GlossaryTerm.domain == domain,
            GlossaryTerm.source_lang == source_lang,
            GlossaryTerm.target_lang == target_lang,
        )
    )
    entries = result.scalars().all()
    if not entries:
        return []

    lowered = text.lower()
    return [
        entry.target_term
        for entry in entries
        if re.search(rf"\b{re.escape(entry.source_term.lower())}\b", lowered)
    ]
