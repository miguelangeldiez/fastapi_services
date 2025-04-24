# routers/posts.py
import uuid
from math import ceil
from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_db_session, current_active_user
from ..db.post_model import Post, Comment, User
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


@router.delete(
    "/delete_post/{post_id}",
    response_model=MessageResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Eliminar una publicación",
)
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    # 1) recuperar
    post = await db.get(Post, post_id)
    if not post or post.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publicación no encontrada o no autorizada."
        )

    try:
        # 2) eliminar
        await db.delete(post)
        # 3) confirmar
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la publicación."
        )

    return MessageResponse(msg="Publicación eliminada con éxito.", data=None)


@router.get(
    "/{post_id}/comments",
    response_model=List[CommentOut],
    summary="Listar comentarios de una publicación",
)
async def get_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
):
    # 1) Traer el post con sus comentarios
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.comments))
        .where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada.")
    return post.comments


@router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse[None],
    summary="Eliminar un comentario por ID",
)
async def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    # 1) Recuperar el comentario
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado.")
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este comentario.")

    try:
        # 2) Eliminar y confirmar
        await db.delete(comment)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el comentario.")

    return MessageResponse(msg="Comentario eliminado con éxito.", data=None)
