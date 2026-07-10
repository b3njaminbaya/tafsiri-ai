from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .... import schemas
from ....deps import get_db, require_role
from ....handles import public_handle
from ....models import BlogPost, User
from ....slugify import unique_slug

router = APIRouter(prefix="/blog", tags=["blog"])


def _read(post: BlogPost) -> schemas.BlogPostRead:
    return schemas.BlogPostRead(
        id=post.id,
        slug=post.slug,
        title=post.title,
        excerpt=post.excerpt,
        category=post.category,
        status=post.status,
        author_handle=public_handle(post.author.display_name, post.author.email),
        published_at=post.published_at,
        created_at=post.created_at,
    )


def _detail(post: BlogPost) -> schemas.BlogPostDetail:
    return schemas.BlogPostDetail(**_read(post).model_dump(), body=post.body)


@router.get(
    "/posts",
    response_model=list[schemas.BlogPostRead],
    summary="List published blog posts",
)
async def list_published_posts(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(BlogPost).options(selectinload(BlogPost.author)).where(
        BlogPost.status == "published"
    )
    if category:
        query = query.where(BlogPost.category == category)
    posts = (
        (await db.execute(query.order_by(BlogPost.published_at.desc())))
        .scalars()
        .all()
    )
    return [_read(post) for post in posts]


@router.get(
    "/posts/{slug}",
    response_model=schemas.BlogPostDetail,
    summary="Get a published blog post by slug",
)
async def get_published_post(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BlogPost)
        .options(selectinload(BlogPost.author))
        .where(BlogPost.slug == slug, BlogPost.status == "published")
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _detail(post)


@router.get(
    "/admin/posts",
    response_model=list[schemas.BlogPostRead],
    summary="List all blog posts, any status (admin only)",
)
async def admin_list_posts(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    posts = (
        (
            await db.execute(
                select(BlogPost)
                .options(selectinload(BlogPost.author))
                .order_by(BlogPost.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    return [_read(post) for post in posts]


async def _get_post_or_404(db: AsyncSession, post_id: int) -> BlogPost:
    result = await db.execute(
        select(BlogPost).options(selectinload(BlogPost.author)).where(BlogPost.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get(
    "/admin/posts/{post_id}",
    response_model=schemas.BlogPostDetail,
    summary="Get any blog post by id, any status (admin only)",
)
async def admin_get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    post = await _get_post_or_404(db, post_id)
    return _detail(post)


@router.post(
    "/admin/posts",
    response_model=schemas.BlogPostDetail,
    summary="Create a blog post (admin only)",
)
async def admin_create_post(
    body: schemas.BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    slug = await unique_slug(db, body.title)
    post = BlogPost(
        author_id=admin.id,
        slug=slug,
        title=body.title,
        excerpt=body.excerpt,
        body=body.body,
        category=body.category,
        status=body.status,
        published_at=datetime.now(timezone.utc) if body.status == "published" else None,
    )
    db.add(post)
    await db.commit()
    post = await _get_post_or_404(db, post.id)
    return _detail(post)


@router.patch(
    "/admin/posts/{post_id}",
    response_model=schemas.BlogPostDetail,
    summary="Update a blog post, including publishing/unpublishing (admin only)",
)
async def admin_update_post(
    post_id: int,
    body: schemas.BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    post = await _get_post_or_404(db, post_id)
    data = body.model_dump(exclude_unset=True)

    if "title" in data and data["title"] != post.title:
        post.title = data["title"]
        post.slug = await unique_slug(db, data["title"], exclude_id=post.id)
    if "excerpt" in data:
        post.excerpt = data["excerpt"]
    if "body" in data:
        post.body = data["body"]
    if "category" in data:
        post.category = data["category"]
    if "status" in data and data["status"] != post.status:
        post.status = data["status"]
        if data["status"] == "published" and post.published_at is None:
            post.published_at = datetime.now(timezone.utc)
        elif data["status"] == "draft":
            post.published_at = None

    await db.commit()
    post = await _get_post_or_404(db, post.id)
    return _detail(post)


@router.delete("/admin/posts/{post_id}", summary="Delete a blog post (admin only)")
async def admin_delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    post = await _get_post_or_404(db, post_id)
    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted"}
