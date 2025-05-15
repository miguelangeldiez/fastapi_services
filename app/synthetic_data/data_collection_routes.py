from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
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
from config import logger

data_router = APIRouter(prefix="/data", tags=["Data Collection"])


# Ruta para obtener usuarios generados por el usuario autenticado
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

    if format == "csv":
        logger.info("Generando archivo CSV para usuarios.")
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "email", "is_active", "is_superuser", "is_verified"])
        writer.writeheader()
        for user in users:
            writer.writerow({
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
            })
        output.seek(0)
        logger.info("Archivo CSV generado con éxito.")
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=users.csv"
        })
    elif format == "pdf":
        logger.info("Generando archivo PDF para usuarios.")
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=36, bottomMargin=36,
            title="Usuarios generados"
        )
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Usuarios generados", styles["Title"]),
            Spacer(1, 12),
        ]
        headers = ["ID", "Email", "Activo", "Verificado", "Superusuario"]
        rows = [headers]
        for u in users:
            rows.append([
                str(u.id),
                u.email,
                "Sí" if u.is_active else "No",
                "Sí" if u.is_verified else "No",
                "Sí" if u.is_superuser else "No",
            ])
        table = Table(rows, repeatRows=1)
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
        logger.info("Archivo PDF generado con éxito.")
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=users.pdf"},
        )
    logger.info("Devolviendo usuarios en formato JSON.")
    return {"data": [user.__dict__ for user in users]}


# Ruta para obtener publicaciones generadas por el usuario autenticado
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

    if format == "csv":
        logger.info("Generando archivo CSV para publicaciones.")
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "title", "content", "is_published", "user_id"])
        writer.writeheader()
        for post in posts:
            writer.writerow({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "is_published": post.is_published,
                "user_id": post.user_id,
            })
        output.seek(0)
        logger.info("Archivo CSV generado con éxito.")
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=posts.csv"
        })
    elif format == "pdf":
        logger.info("Generando archivo PDF para publicaciones.")
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=36, bottomMargin=36,
            title="Posts generados"
        )
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Posts generados", styles["Title"]),
            Spacer(1, 12),
        ]
        headers = ["ID", "Titulo", "Publicado"]
        rows = [headers]
        for p in posts:
            rows.append([
                str(p.id),
                p.title,
                "Sí" if p.is_published else "No"
            ])
        table = Table(rows, repeatRows=1)
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
        logger.info("Archivo PDF generado con éxito.")
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=posts.pdf"},
        )
    logger.info("Devolviendo publicaciones en formato JSON.")
    return {"data": [post.__dict__ for post in posts]}


# Ruta para obtener comentarios generados por el usuario autenticado
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

    if format == "csv":
        logger.info("Generando archivo CSV para comentarios.")
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "content", "post_id", "user_id"])
        writer.writeheader()
        for comment in comments:
            writer.writerow({
                "id": comment.id,
                "content": comment.content,
                "post_id": comment.post_id,
                "user_id": comment.user_id,
            })
        output.seek(0)
        logger.info("Archivo CSV generado con éxito.")
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=comments.csv"
        })
    elif format == "pdf":
        logger.info("Generando archivo PDF para comentarios.")
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=36, bottomMargin=36,
            title="Comentarios generados"
        )
        styles = getSampleStyleSheet()
        elements = [
            Paragraph("Comentarios generados", styles["Title"]),
            Spacer(1, 12),
        ]
        headers = ["ID", "Contenido", "Post ID"]
        rows = [headers]
        for c in comments:
            rows.append([
                str(c.id),
                c.content,
                str(c.post_id)
            ])
        table = Table(rows, repeatRows=1)
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
        logger.info("Archivo PDF generado con éxito.")
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=comments.pdf"},
        )
    logger.info("Devolviendo comentarios en formato JSON.")
    return {"data": [comment.__dict__ for comment in comments]}


# Ruta para obtener todos los batch_id del usuario autenticado
@data_router.get("/batches", summary="Obtener todos los batch_id del usuario autenticado")
async def get_batches(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(current_active_user),
):
    logger.info(f"Obteniendo batch_ids para el usuario autenticado: {current_user.id}")
    query = await session.execute(
        select(Batch.batch_id).where(User.id == current_user.id).distinct()
    )
    user_batches = query.scalars().all()
    logger.info(f"Batch_ids de usuarios obtenidos: {user_batches}")

    query = await session.execute(
        select(Post.batch_id).where(Post.user_id == current_user.id).distinct()
    )
    post_batches = query.scalars().all()
    logger.info(f"Batch_ids de publicaciones obtenidos: {post_batches}")

    query = await session.execute(
        select(Comment.batch_id).where(Comment.user_id == current_user.id).distinct()
    )
    comment_batches = query.scalars().all()
    logger.info(f"Batch_ids de comentarios obtenidos: {comment_batches}")

    all_batches = set(user_batches + post_batches + comment_batches)
    logger.info(f"Todos los batch_ids combinados: {all_batches}")

    return {"batches": list(all_batches)}