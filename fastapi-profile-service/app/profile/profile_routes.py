# app/users/routes.py
from math import ceil
import uuid
from typing import List, Generic, TypeVar
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_db_session, current_active_user
from ..db.models import User ,Post  
from .schemas import PaginatedPostsResponse,UserRead



router = APIRouter(prefix="/user", tags=["user"],dependencies=[Depends(current_active_user)])

@router.get(
    "/profile",
    response_model=UserRead,
    summary="Obtener perfil del usuario autenticado",
)
async def profile(user: User = Depends(current_active_user)):
    """
    Devuelve los datos (id, username, email, etc.) del usuario actualmente autenticado.
    """
    return user


@router.get(
    "/{user_id}/posts",
    response_model=PaginatedPostsResponse,
    summary="Listar posts del usuario autenticado",
)
async def get_user_posts(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
    page: int = 1,
    per_page: int = 10,
):
    """
    Sólo permite al usuario autenticado ver sus propios posts.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso no autorizado",
        )

    # total de posts
    total_q = await db.execute(
        select(func.count()).select_from(Post).where(Post.user_id== user_id)
    )
    total = total_q.scalar_one()

    # páginas totales
    pages = (total + per_page - 1) // per_page

    # consulta paginada
    stmt = (
        select(Post)
        .where(Post.user_id== user_id)
        .order_by(Post.created_at.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return PaginatedPostsResponse(
        posts=posts,  # lista de PostOut
        total=total,  # conteo total de registros
        pages=ceil(total / per_page),  # total de páginas
        current_page=page,  # página actual
        per_page=per_page,  # elementos por página
        has_next=(page * per_page) < total,  # hay siguiente?
        has_prev=page > 1,  # hay anterior?
    )
