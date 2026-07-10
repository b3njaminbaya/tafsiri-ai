from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .... import schemas
from ....deps import get_db, require_role
from ....models import Role, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/users",
    response_model=list[schemas.AdminUserRead],
    summary="List all registered users (admin only)",
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    result = await db.execute(
        select(User).options(selectinload(User.role)).order_by(User.id.asc())
    )
    return result.scalars().all()


@router.patch(
    "/users/{user_id}",
    response_model=schemas.AdminUserRead,
    summary="Change a user's role and/or active status (admin only)",
)
async def update_user(
    user_id: int,
    body: schemas.AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == admin.id and body.is_active is False:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")

    if body.role_name is not None:
        role = (
            await db.execute(select(Role).where(Role.name == body.role_name))
        ).scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=400, detail="Unknown role")
        user.role = role

    if body.is_active is not None:
        user.is_active = body.is_active

    await db.commit()
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    return result.scalar_one()
