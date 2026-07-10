from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .... import schemas
from ....deps import get_current_active_user, get_db
from ....handles import public_handle
from ....models import ForumPost, ForumReply, User

router = APIRouter(prefix="/forum", tags=["forum"])


def _post_read(post: ForumPost) -> schemas.ForumPostRead:
    return schemas.ForumPostRead(
        id=post.id,
        category=post.category,
        title=post.title,
        author_handle=public_handle(post.author.display_name, post.author.email),
        reply_count=len(post.replies),
        created_at=post.created_at,
    )


def _reply_read(reply: ForumReply) -> schemas.ForumReplyRead:
    return schemas.ForumReplyRead(
        id=reply.id,
        post_id=reply.post_id,
        author_handle=public_handle(reply.author.display_name, reply.author.email),
        body=reply.body,
        created_at=reply.created_at,
    )


@router.get(
    "/categories",
    response_model=list[schemas.ForumCategoryCount],
    summary="Post counts per forum category",
)
async def forum_categories(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(ForumPost.category, func.count(ForumPost.id)).group_by(ForumPost.category)
        )
    ).all()
    counts = {category: count for category, count in rows}
    return [
        schemas.ForumCategoryCount(category=category, post_count=counts.get(category, 0))
        for category in schemas.FORUM_CATEGORIES
    ]


@router.get(
    "/posts",
    response_model=list[schemas.ForumPostRead],
    summary="List forum posts, most recent first, optionally filtered by category",
)
async def list_posts(
    category: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    query = select(ForumPost).options(
        selectinload(ForumPost.author), selectinload(ForumPost.replies)
    )
    if category:
        query = query.where(ForumPost.category == category)
    query = query.order_by(ForumPost.id.desc()).limit(limit)
    posts = (await db.execute(query)).scalars().all()
    return [_post_read(post) for post in posts]


@router.post(
    "/posts",
    response_model=schemas.ForumPostRead,
    summary="Start a new forum discussion",
)
async def create_post(
    body: schemas.ForumPostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    post = ForumPost(
        author_id=user.id, category=body.category, title=body.title, body=body.body
    )
    db.add(post)
    await db.commit()
    result = await db.execute(
        select(ForumPost)
        .options(selectinload(ForumPost.author), selectinload(ForumPost.replies))
        .where(ForumPost.id == post.id)
    )
    return _post_read(result.scalar_one())


async def _get_post_or_404(db: AsyncSession, post_id: int) -> ForumPost:
    result = await db.execute(
        select(ForumPost)
        .options(
            selectinload(ForumPost.author),
            selectinload(ForumPost.replies).selectinload(ForumReply.author),
        )
        .where(ForumPost.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get(
    "/posts/{post_id}",
    response_model=schemas.ForumPostDetail,
    summary="Get a forum post with its replies",
)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await _get_post_or_404(db, post_id)
    return schemas.ForumPostDetail(
        id=post.id,
        category=post.category,
        title=post.title,
        body=post.body,
        author_handle=public_handle(post.author.display_name, post.author.email),
        created_at=post.created_at,
        replies=[_reply_read(reply) for reply in post.replies],
    )


@router.post(
    "/posts/{post_id}/replies",
    response_model=schemas.ForumReplyRead,
    summary="Reply to a forum post",
)
async def create_reply(
    post_id: int,
    body: schemas.ForumReplyCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    await _get_post_or_404(db, post_id)
    reply = ForumReply(post_id=post_id, author_id=user.id, body=body.body)
    db.add(reply)
    await db.commit()
    result = await db.execute(
        select(ForumReply).options(selectinload(ForumReply.author)).where(ForumReply.id == reply.id)
    )
    return _reply_read(result.scalar_one())
