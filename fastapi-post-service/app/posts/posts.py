# routers/posts.py
import uuid
from math import ceil
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_db_session, current_active_user
from ..db.post import Post, Comment, User
from .schemas import (
    PostCreate,
    PostOut,
    CommentOut,
    PaginatedPostsResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/posts", tags=["posts"], dependencies=[Depends(current_active_user)]
)


@router.get(
    "/all_posts",
    response_model=PaginatedPostsResponse,
    summary="Listar todas las publicaciones paginadas",
)
async def get_all_posts(
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db_session),
) -> PaginatedPostsResponse:
    total_stmt = select(func.count()).select_from(Post)
    total_result = await db.execute(total_stmt)
    total = total_result.scalar_one()

    stmt = (
        select(Post)
        .options(
            selectinload(Post.comments),
            selectinload(Post.author),
        )
        .offset((page - 1) * per_page)
        .limit(per_page)
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


@router.post(
    "/create_post",
    response_model=MessageResponse[PostOut],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva publicación",
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
        author_id=user.id,
    )
    db.add(new_post)
    try:
        # fuerza el INSERT
        await db.flush()              
        # confirma la transacción
        await db.commit()             
        # recarga el objeto con valores de BD
        await db.refresh(new_post)    
    except Exception as e:
        # revierte si algo falla
        await db.rollback()           
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la publicación: {e}"
        )
    return MessageResponse(msg="Publicación creada con éxito.", data=new_post)


@router.delete(
    "/delete_post/{post_id}",
    response_model=MessageResponse[None],
    summary="Eliminar una publicación por ID",
)
def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    post = db.query(Post).get(post_id)
    if not post:
        raise HTTPException(404, "Publicación no encontrada.")
    if post.user_id != user.id:
        raise HTTPException(403, "No tienes permiso para eliminar esta publicación.")
    try:
        db.delete(post)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(500, "Error al eliminar la publicación.")
    return MessageResponse(msg="Publicación eliminada con éxito.")


@router.get(
    "/{post_id}/comments",
    response_model=List[CommentOut],
    summary="Listar comentarios de una publicación",
)
def get_comments(post_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)):
    post = db.query(Post).options(joinedload(Post.comments)).get(post_id)
    if not post:
        raise HTTPException(404, "Publicación no encontrada.")
    return post.comments


@router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse[None],
    summary="Eliminar un comentario por ID",
)
def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    comment = db.query(Comment).get(comment_id)
    if not comment:
        raise HTTPException(404, "Comentario no encontrado.")
    if comment.user_id != user.id:
        raise HTTPException(403, "No tienes permiso para eliminar este comentario.")
    try:
        db.delete(comment)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(500, "Error al eliminar el comentario.")
    return MessageResponse(msg="Comentario eliminado con éxito.")
