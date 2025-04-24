# routers/posts.py
import uuid
from math import ceil
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_db_session,current_active_user
from ..db.post import Post, Comment, User
from .schemas import (
    PostCreate, PostOut, CommentOut,
    PaginatedPostsResponse, MessageResponse
)

router = APIRouter(prefix="/posts", tags=["posts"],dependencies=[Depends(current_active_user)])


@router.get(
    "/all_posts",
    response_model=PaginatedPostsResponse,
    summary="Listar todas las publicaciones paginadas"
)
def get_all_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession= Depends(get_db_session)
):
    # Query con joinedload para cargar usuario, likes y comentarios
    base_q = db.query(Post).options(
        joinedload(Post.user),
        joinedload(Post.likes),
        joinedload(Post.comments)
    )
    total = base_q.count()
    posts = (
        base_q
        .order_by(Post.timestamp.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return PaginatedPostsResponse(
        posts=posts,
        total=total,
        pages=ceil(total / per_page),
        current_page=page,
        per_page=per_page,
        has_next=page * per_page < total,
        has_prev=page > 1
    )


@router.post(
    "/create_post",
    response_model=MessageResponse[PostOut],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva publicación"
)
def create_post(
    payload: PostCreate,
    db: AsyncSession= Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    new_post = Post(content=payload.content, user_id=user.id)
    db.add(new_post)
    try:
        db.commit()
        db.refresh(new_post)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la publicación."
        )
    return MessageResponse(
        msg="Publicación creada con éxito.",
        data=new_post
    )


@router.delete(
    "/delete_post/{post_id}",
    response_model=MessageResponse[None],
    summary="Eliminar una publicación por ID"
)
def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession= Depends(get_db_session),
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
    summary="Listar comentarios de una publicación"
)
def get_comments(
    post_id: uuid.UUID,
    db: AsyncSession= Depends(get_db_session)
):
    post = (
        db.query(Post)
        .options(joinedload(Post.comments))
        .get(post_id)
    )
    if not post:
        raise HTTPException(404, "Publicación no encontrada.")
    return post.comments


@router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse[None],
    summary="Eliminar un comentario por ID"
)
def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession= Depends(get_db_session),
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
