from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .... import schemas
from ....deps import get_db, require_role
from ....models import GlossaryTerm, User

router = APIRouter(prefix="/glossary", tags=["glossary"])


@router.get(
    "/",
    response_model=list[schemas.GlossaryTermRead],
    summary="List domain glossary terms, optionally filtered",
)
async def list_glossary_terms(
    domain: Optional[str] = None,
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(GlossaryTerm)
    if domain:
        query = query.where(GlossaryTerm.domain == domain)
    if source_lang:
        query = query.where(GlossaryTerm.source_lang == source_lang)
    if target_lang:
        query = query.where(GlossaryTerm.target_lang == target_lang)
    result = await db.execute(query.order_by(GlossaryTerm.id.desc()))
    return result.scalars().all()


@router.post(
    "/",
    response_model=schemas.GlossaryTermRead,
    summary="Add a glossary term (admin only)",
)
async def create_glossary_term(
    body: schemas.GlossaryTermCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    term = GlossaryTerm(
        domain=body.domain,
        source_lang=body.source_lang,
        target_lang=body.target_lang,
        source_term=body.source_term,
        target_term=body.target_term,
        created_by_id=admin.id,
    )
    db.add(term)
    await db.commit()
    return term


@router.delete("/{term_id}", summary="Delete a glossary term (admin only)")
async def delete_glossary_term(
    term_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    result = await db.execute(select(GlossaryTerm).where(GlossaryTerm.id == term_id))
    term = result.scalar_one_or_none()
    if not term:
        raise HTTPException(status_code=404, detail="Glossary term not found")
    await db.delete(term)
    await db.commit()
    return {"message": "Glossary term deleted"}
