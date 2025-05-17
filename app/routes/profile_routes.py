from math import ceil
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main_db import get_db_session
from app.routes.auth_routes import current_active_user
from app.db.models import User, Post
from .schemas import PaginatedPostsResponse, UserRead
from app.config import logger

profile_router = APIRouter(
    prefix="/user",
    tags=["Profile Settings"],
    dependencies=[Depends(current_active_user)]
)

@profile_router.get(
    "/profile",
    response_model=UserRead,
    summary="Obtener perfil del usuario autenticado",
)
async def profile(user: User = Depends(current_active_user)):
    """
    Devuelve los datos (id, username, email, etc.) del usuario actualmente autenticado.
    """
    return user

@profile_router.get(
    "/{user_id}/posts",
    response_model=PaginatedPostsResponse,
    summary="Listar posts del usuario autenticado",
)
async def get_user_posts(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    """
    Sólo permite al usuario autenticado ver sus propios posts.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso no autorizado",
        )

    total_q = await db.execute(
        select(func.count()).select_from(Post).where(Post.user_id == user_id)
    )
    total = total_q.scalar_one()

    stmt = (
        select(Post)
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    pages = ceil(total / per_page) if per_page else 1

    return PaginatedPostsResponse(
        posts=posts,
        total=total,
        pages=pages,
        current_page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1,
    )
