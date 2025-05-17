from uuid import UUID
from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from io import StringIO, BytesIO
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from app.db.models import Batch, User, Post, Comment
from app.db.main_db import get_db_session
from app.routes.auth_routes import current_active_user
from app.config import logger

data_router = APIRouter(prefix="/data", tags=["Data Collection"])

def _to_dict_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
    }

def _to_dict_post(post: Post) -> dict:
    return {
        "id": str(post.id),
        "title": post.title,
        "content": post.content,
        "is_published": post.is_published,
        "user_id": str(post.user_id),
    }

def _to_dict_comment(comment: Comment) -> dict:
    return {
        "id": str(comment.id),
        "content": comment.content,
        "post_id": str(comment.post_id),
        "user_id": str(comment.user_id),
    }

def _csv_response(data: list, fieldnames: list, filename: str):
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

def _pdf_response(title: str, headers: list, rows: list, filename: str):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36, rightMargin=36,
        topMargin=36, bottomMargin=36,
        title=title
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 12),
    ]
    table = Table([headers] + rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

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
    data = [_to_dict_user(u) for u in users]

    if format == "csv":
        return _csv_response(data, ["id", "email", "is_active", "is_superuser", "is_verified"], "users.csv")
    elif format == "pdf":
        rows = [[d["id"], d["email"], "Sí" if d["is_active"] else "No", "Sí" if d["is_verified"] else "No", "Sí" if d["is_superuser"] else "No"] for d in data]
        return _pdf_response("Usuarios generados", ["ID", "Email", "Activo", "Verificado", "Superusuario"], rows, "users.pdf")
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
    data = [_to_dict_post(p) for p in posts]

    if format == "csv":
        return _csv_response(data, ["id", "title", "content", "is_published", "user_id"], "posts.csv")
    elif format == "pdf":
        rows = [[d["id"], d["title"], "Sí" if d["is_published"] else "No"] for d in data]
        return _pdf_response("Posts generados", ["ID", "Titulo", "Publicado"], rows, "posts.pdf")
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
    data = [_to_dict_comment(c) for c in comments]

    if format == "csv":
        return _csv_response(data, ["id", "content", "post_id", "user_id"], "comments.csv")
    elif format == "pdf":
        rows = [[d["id"], d["content"], d["post_id"]] for d in data]
        return _pdf_response("Comentarios generados", ["ID", "Contenido", "Post ID"], rows, "comments.pdf")
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