from uuid import UUID
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join


from app.db import Batch, User, Post, Comment,get_db_session
from app.services.auth_service import current_active_user
from app.config import logger
from app.services.data_collection_service import csv_response, pdf_response, to_dict_comment, to_dict_post, to_dict_user

data_router = APIRouter(prefix="/data", tags=["Data Collection"])

@data_router.get("/users", summary="Obtener usuario dueño del batch")
async def get_users(
    batch_id: UUID = Query(..., description="Identificador del lote"),
    format: str = Query("json", enum=["json", "csv", "pdf"]),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    logger.info(f"Obteniendo usuario para batch_id: {batch_id} en formato: {format}")
    batch = await session.get(Batch, batch_id)
    if not batch or batch.user_id != current_user.id:
        logger.info("Batch no encontrado o no pertenece al usuario autenticado.")
        return {"data": []}

    user = await session.get(User, batch.user_id)
    if not user:
        logger.info("Usuario no encontrado para el batch.")
        return {"data": []}

    data = [to_dict_user(user)]

    if format == "csv":
        return csv_response(data, ["id", "email", "is_active", "is_superuser", "is_verified"], "users.csv")
    elif format == "pdf":
        rows = [[d["id"], d["email"], "Sí" if d["is_active"] else "No", "Sí" if d["is_verified"] else "No", "Sí" if d["is_superuser"] else "No"] for d in data]
        return pdf_response("Usuarios generados", ["ID", "Email", "Activo", "Verificado", "Superusuario"], rows, "users.pdf")
    return {"data": data}

@data_router.get("/posts", summary="Obtener publicaciones generadas")
async def get_posts(
    batch_id: UUID = Query(..., description="Identificador del lote"),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    # Busca el batch y su user_id
    batch = await session.get(Batch, batch_id)
    if not batch or batch.user_id != current_user.id:
        return {"data": []}
    # Busca los posts del usuario que creó el batch
    query = await session.execute(
        select(Post).where(Post.user_id == batch.user_id)
    )
    posts = query.scalars().all()
    data = [to_dict_post(p) for p in posts]
    return {"data": data}

@data_router.get("/comments", summary="Obtener comentarios generados")
async def get_comments(
    batch_id: UUID = Query(..., description="Identificador del lote"),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    batch = await session.get(Batch, batch_id)
    if not batch or batch.user_id != current_user.id:
        return {"data": []}
    # Busca los comentarios de los posts del usuario que creó el batch
    posts_query = await session.execute(
        select(Post.id).where(Post.user_id == batch.user_id)
    )
    post_ids = [pid for pid, in posts_query.all()]
    if not post_ids:
        return {"data": []}
    comments_query = await session.execute(
        select(Comment).where(Comment.post_id.in_(post_ids))
    )
    comments = comments_query.scalars().all()
    data = [to_dict_comment(c) for c in comments]
    return {"data": data}

@data_router.get("/batches", summary="Obtener todos los batch_id del usuario autenticado")
async def get_batches(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    logger.info(f"Obteniendo batch_ids para el usuario autenticado: {current_user.id}")

    # Corrige el select para obtener los batch_id correctos
    user_batches = await session.execute(
        select(Batch.id).where(Batch.user_id == current_user.id).distinct()
    )
    post_batches = await session.execute(
        select(Post.batch_id).where(Post.user_id == current_user.id).distinct()
    )
    comment_batches = await session.execute(
        select(Comment.batch_id).where(Comment.user_id == current_user.id).distinct()
    )

    # Filtra None y convierte a set para evitar duplicados
    all_batches = set(
        filter(None, user_batches.scalars().all() + post_batches.scalars().all() + comment_batches.scalars().all())
    )
    logger.info(f"Todos los batch_ids combinados: {all_batches}")

    return {"batches": list(all_batches)}