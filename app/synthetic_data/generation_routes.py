from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from faker import Faker
import httpx
import asyncio
import uuid

from app.synthetic_data.schemas import CommentRequest, PostRequest, UserRequest
from app.routes.auth_routes import current_active_user
from app.db.models import Batch, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.main_db import get_db_session
from app.real_time.websockets_routes import broadcast_message

fake = Faker()
synthetic_router = APIRouter(prefix="/synthetic", tags=["Synthetic Data Generation"])


# Función para extraer el token de la cookie
def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("threadfit_cookie")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no encontrado en las cookies.",
        )
    return token


@synthetic_router.post("/users", summary="Generar y registrar usuarios ficticios")
async def generate_users(
    request: UserRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    if request.seed is not None:
        Faker.seed(request.seed)

    batch_id = str(uuid.uuid4())  # Generar un identificador único para el lote

    # Crear un nuevo lote y asociarlo al usuario actual
    new_batch = Batch(id=batch_id, user_id=current_user.id)
    db.add(new_batch)
    await db.commit()

    generated_users = []  # Almacenar los usuarios generados para el modo pull

    async with httpx.AsyncClient() as client:
        for _ in range(request.num_users):
            user_data = {
                "email": fake.email(),
                "password": fake.password(length=10),
                "batch_id": batch_id,  # Asociar el lote al usuario
            }
            user_response = await client.post(
                "http://localhost:8000/auth/register",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            if user_response.status_code != 201:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al registrar usuario: {user_response.text}",
                )
            generated_users.append(user_data)  # Agregar al modo pull
            if request.mode == "push":
                # Notificar al cliente sobre el nuevo usuario generado
                await broadcast_message(f"Nuevo usuario generado: {user_data['email']}")
            await asyncio.sleep(1.0 / request.speed_multiplier)

    if request.mode == "pull":
        return {"msg": f"{request.num_users} usuarios registrados con éxito.", "batch_id": batch_id, "data": generated_users}
    return {"msg": f"{request.num_users} usuarios registrados con éxito.", "batch_id": batch_id}


@synthetic_router.post("/posts", summary="Generar y registrar publicaciones ficticias")
async def generate_posts(
    request: PostRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    if request.seed is not None:
        Faker.seed(request.seed)

    # Crear un nuevo lote y asociarlo al usuario actual
    new_batch = Batch(user_id=current_user.id)
    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)  # Refrescar para obtener el ID generado

    generated_posts = []  # Almacenar las publicaciones generadas para el modo pull

    async with httpx.AsyncClient() as client:
        for _ in range(request.num_posts):
            post_data = {
                "title": fake.sentence(),
                "content": fake.paragraph(),
                "is_published": True,
                "user_id": request.user_id,
                "batch_id": str(new_batch.id),  # Asociar el lote a la publicación
            }
            post_response = await client.post(
                "http://localhost:8000/posts/create_post",
                json=post_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            if post_response.status_code != 201:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al crear publicación: {post_response.text}",
                )
            generated_posts.append(post_data)  # Agregar al modo pull
            if request.mode == "push":
                # Notificar al cliente sobre la nueva publicación generada
                await broadcast_message(f"Nueva publicación generada: {post_data['title']}")
            await asyncio.sleep(1.0 / request.speed_multiplier)

    if request.mode == "pull":
        return {"msg": f"{request.num_posts} publicaciones registradas con éxito.", "batch_id": str(new_batch.id), "data": generated_posts}
    return {"msg": f"{request.num_posts} publicaciones registradas con éxito.", "batch_id": str(new_batch.id)}


@synthetic_router.post("/comments", summary="Generar y registrar comentarios ficticios")
async def generate_comments(
    request: CommentRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    if request.seed is not None:
        Faker.seed(request.seed)

    # Crear un nuevo lote y asociarlo al usuario actual
    new_batch = Batch(user_id=current_user.id)
    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)  # Refrescar para obtener el ID generado

    generated_comments = []  # Almacenar los comentarios generados para el modo pull

    async with httpx.AsyncClient() as client:
        for _ in range(request.num_comments):
            comment_data = {
                "content": fake.sentence(),
                "post_id": request.post_id,
                "batch_id": str(new_batch.id),  # Asociar el lote al comentario
            }
            comment_response = await client.post(
                f"http://localhost:8000/interactions/{request.post_id}/comments",
                json=comment_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            if comment_response.status_code != 201:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al agregar comentario: {comment_response.text}",
                )
            generated_comments.append(comment_data)  # Agregar al modo pull
            if request.mode == "push":
                # Notificar al cliente sobre el nuevo comentario generado
                await broadcast_message(f"Nuevo comentario generado: {comment_data['content']}")
            await asyncio.sleep(1.0 / request.speed_multiplier)

    if request.mode == "pull":
        return {"msg": f"{request.num_comments} comentarios registrados con éxito.", "batch_id": str(new_batch.id), "data": generated_comments}
    return {"msg": f"{request.num_comments} comentarios registrados con éxito.", "batch_id": str(new_batch.id)}