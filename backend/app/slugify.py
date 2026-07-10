import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import BlogPost


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "post"


async def unique_slug(db: AsyncSession, title: str, exclude_id: int | None = None) -> str:
    base = slugify(title)
    candidate = base
    suffix = 2
    while True:
        query = select(BlogPost.id).where(BlogPost.slug == candidate)
        if exclude_id is not None:
            query = query.where(BlogPost.id != exclude_id)
        existing = (await db.execute(query)).scalar_one_or_none()
        if not existing:
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1
