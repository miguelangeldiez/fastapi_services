import uuid
from math import ceil
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from config import logger
from app.db.main_db import get_db_session
from app.routes.auth_routes import current_active_user
from app.db.models import Post, User
from .schemas import (
    PostCreate,
    PostOut,
    PaginatedPostsResponse,
    MessageResponse,
)

posts_router = APIRouter(
    prefix="/posts", tags=["Posts Settings"]
)


@posts_router.get(
    "/all_posts",
    response_model=PaginatedPostsResponse,
    summary="Listar todas las publicaciones paginadas",
)
async def get_all_posts(
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedPostsResponse:
    logger.info(f"Solicitud para listar publicaciones: page={page}, per_page={per_page}")
    total_stmt = select(func.count()).select_from(Post)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()
    logger.info(f"Total de publicaciones: {total}")

    stmt = (
        select(Post)
        .options(
            selectinload(Post.comments),
            selectinload(Post.user),
        )
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()
    logger.info(f"Publicaciones obtenidas: {len(posts)}")

    return PaginatedPostsResponse(
        posts=posts,
        total=total,
        pages=ceil(total / per_page),
        current_page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1,
    )


@posts_router.post(
    "/create_post",
    response_model=MessageResponse[PostOut],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva publicación",
    dependencies=[Depends(current_active_user)],
)
async def create_post(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    new_post = Post(
        title=payload.title,
        content=payload.content,
        is_published=payload.is_published,
        user_id=user.id,
    )
    
    try:
        db.add(new_post)
        # fuerza el INSERT
        await db.flush()              
        # confirma la transacción
        await db.commit()             
        # recarga el objeto con valores de BD
        await db.refresh(new_post)    
    except Exception as e:
        import traceback; traceback.print_exc()
        # revierte si algo falla
        await db.rollback()           
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la publicación: {e}"
        )
  
    return MessageResponse(msg="Publicación creada con éxito.", data=new_post)


@posts_router.delete(
    "/delete_post/{post_id}",
    response_model=MessageResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Eliminar una publicación",
    dependencies=[Depends(current_active_user)],
)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    post = await db.get(Post, post_id)
    if not post or post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicación no encontrada o no autorizada."
        )
    try:
        await db.delete(post)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la publicación."
        )

    return MessageResponse(msg="Publicación eliminada con éxito.", data=None)
