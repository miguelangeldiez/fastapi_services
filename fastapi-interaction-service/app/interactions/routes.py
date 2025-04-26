import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import  WebSocket, WebSocketDisconnect
from app.socket.manage import manager, notify_new_comment, notify_new_like

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_db_session, current_active_user
from ..db.models import Post, Comment, Like, User
from .schemas import (
    CommentOut,
    MessageResponse,
)

interactions_router = APIRouter(
    prefix="/posts", dependencies=[Depends(current_active_user)]
)

@interactions_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint para manejar conexiones WebSocket.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Mensaje recibido: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Cliente desconectado")

@interactions_router.get(
    "/{post_id}/comments",
    response_model=List[CommentOut],
    summary="Listar comentarios de una publicación",
)
async def get_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
) -> List[CommentOut]:
    """
    Devuelve los comentarios de una publicación específica.
    """
    result = await db.execute(
        select(Post).options(selectinload(Post.comments)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada.")
    return post.comments

@interactions_router.post(
    "/{post_id}/comments",
    response_model=MessageResponse[CommentOut],
    status_code=status.HTTP_201_CREATED,
    summary="Publicar un comentario en una publicación",
)
async def post_comment(
    post_id: uuid.UUID,
    comment_data: CommentOut,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    """
    Permite al usuario autenticado publicar un comentario en una publicación específica.
    """
    # Verificar si el post existe
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada.")

    # Crear el comentario
    new_comment = Comment(
        post_id=post_id,
        user_id=user.id,
        content=comment_data.content,
    )
    db.add(new_comment)
    try:
        await db.commit()
        await db.refresh(new_comment)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al publicar el comentario: {e}"
        )
    await notify_new_comment(post_id=str(post_id), comment_id=str(new_comment.id), user_id=str(user.id))
    return MessageResponse(
        msg="Comentario publicado con éxito.",
        data=new_comment,
    )

@interactions_router.post(
    "/{post_id}/like",
    response_model=MessageResponse[None],
    summary="Dar like a una publicación",
)
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    """
    Permite al usuario autenticado dar like a una publicación.
    """
    # Verificar si el post existe
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada.")

    # Verificar si el like ya existe
    existing_like = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user.id)
    )
    if existing_like.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Ya has dado like a esta publicación."
        )

    # Crear el like
    new_like = Like(post_id=post_id, user_id=user.id)
    db.add(new_like)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al dar like a la publicación: {e}"
        )
    await notify_new_like(post_id=str(post_id), user_id=str(user.id))
    return MessageResponse(msg="Like agregado con éxito.", data=None)

@interactions_router.delete(
    "/{post_id}/like",
    response_model=MessageResponse[None],
    summary="Quitar like de una publicación",
)
async def unlike_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    """
    Permite al usuario autenticado quitar su like de una publicación.
    """
    # Verificar si el like existe
    like = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user.id)
    )
    like = like.scalar_one_or_none()
    if not like:
        raise HTTPException(
            status_code=404, detail="No has dado like a esta publicación."
        )

    # Eliminar el like
    try:
        await db.delete(like)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al quitar el like de la publicación: {e}"
        )

    return MessageResponse(msg="Like eliminado con éxito.", data=None)

@interactions_router.delete(
    "/comments/{comment_id}",
    response_model=MessageResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Eliminar un comentario por ID",
)
async def delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(current_active_user),
):
    """
    Permite al usuario autenticado eliminar un comentario por su ID.
    Solo el autor del comentario o un administrador puede eliminarlo.
    """
    # Verificar si el comentario existe
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado.")

    # Verificar si el usuario es el autor del comentario o un administrador
    if comment.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="No tienes permiso para eliminar este comentario."
        )

    # Eliminar el comentario
    try:
        await db.delete(comment)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar el comentario: {e}"
        )

    return MessageResponse(msg="Comentario eliminado con éxito.", data=None)