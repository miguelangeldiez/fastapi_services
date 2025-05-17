from uuid import UUID
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.db.models import Batch, User, Post, Comment
from app.db.main_db import get_db_session
from app.services.auth_service import current_active_user
from app.config import logger
from app.services.data_collection_service import csv_response, pdf_response, to_dict_comment, to_dict_post, to_dict_user

data_router = APIRouter(prefix="/data", tags=["Data Collection"])

@data_router.get("/users", summary="Obtener usuarios generados")
async def get_users(
    batch_id: UUID = Query(..., description="Identificador del lote"),
    format: str = Query("json", enum=["json", "csv", "pdf"]),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    logger.info(f"Obteniendo usuarios generados para batch_id: {batch_id} en formato: {format}")
    query = await session.execute(
        select(User).where(User.batch_id == batch_id)
    )
    users = query.scalars().all()
    logger.info(f"Usuarios obtenidos: {len(users)}")
    data = [to_dict_user(u) for u in users]

    if format == "csv":
        return csv_response(data, ["id", "email", "is_active", "is_superuser", "is_verified"], "users.csv")
    elif format == "pdf":
        rows = [[d["id"], d["email"], "Sí" if d["is_active"] else "No", "Sí" if d["is_verified"] else "No", "Sí" if d["is_superuser"] else "No"] for d in data]
        return pdf_response("Usuarios generados", ["ID", "Email", "Activo", "Verificado", "Superusuario"], rows, "users.pdf")
    return {"data": data}

@data_router.get("/posts", summary="Obtener publicaciones generadas")
async def get_posts(
    batch_id: UUID = Query(..., description="Identificador del lote"),
    format: str = Query("json", enum=["json", "csv", "pdf"]),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    logger.info(f"Obteniendo publicaciones generadas para batch_id: {batch_id} en formato: {format}")
    query = await session.execute(select(Post).where(Post.batch_id == batch_id))
    posts = query.scalars().all()
    logger.info(f"Publicaciones obtenidas: {len(posts)}")
    data = [to_dict_post(p) for p in posts]

    if format == "csv":
        return csv_response(data, ["id", "title", "content", "is_published", "user_id"], "posts.csv")
    elif format == "pdf":
        rows = [[d["id"], d["title"], "Sí" if d["is_published"] else "No"] for d in data]
        return pdf_response("Posts generados", ["ID", "Titulo", "Publicado"], rows, "posts.pdf")
    return {"data": data}

@data_router.get("/comments", summary="Obtener comentarios generados")
async def get_comments(
    batch_id: UUID = Query(..., description="Identificador del lote"),
    format: str = Query("json", enum=["json", "csv", "pdf"]),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    logger.info(f"Obteniendo comentarios generados para batch_id: {batch_id} en formato: {format}")
    query = await session.execute(select(Comment).where(Comment.batch_id == batch_id))
    comments = query.scalars().all()
    logger.info(f"Comentarios obtenidos: {len(comments)}")
    data = [to_dict_comment(c) for c in comments]

    if format == "csv":
        return csv_response(data, ["id", "content", "post_id", "user_id"], "comments.csv")
    elif format == "pdf":
        rows = [[d["id"], d["content"], d["post_id"]] for d in data]
        return pdf_response("Comentarios generados", ["ID", "Contenido", "Post ID"], rows, "comments.pdf")
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