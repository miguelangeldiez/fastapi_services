from typing import Any, AsyncIterator, Dict
from fastapi import APIRouter, HTTPException, status, Depends, Request
from faker import Faker
import httpx
import asyncio
import uuid

from app.synthetic_data.schemas import CommentRequest, PostRequest, UserRequest
from app.routes.auth_routes import current_active_user
from app.db.models import Batch, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.main_db import get_db_session, async_session
from app.synthetic_data import fake, get_token_from_cookie
from config import get_settings, logger

synthetic_router = APIRouter(prefix="/synthetic", tags=["Synthetic Data Generation"])
settings = get_settings()

@synthetic_router.post("/users", summary="Generar y registrar usuarios ficticios")
async def generate_users(
    request: UserRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    logger.info(f"Iniciando generación de usuarios ficticios. Solicitud: {request}")
    if request.seed is not None:
        Faker.seed(request.seed)
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = str(uuid.uuid4())
    logger.info(f"Creando nuevo batch con ID: {batch_id}")

    new_batch = Batch(id=batch_id, user_id=current_user.id)
    db.add(new_batch)
    await db.commit()
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_users = []

    async with httpx.AsyncClient() as client:
        for i in range(request.num_users):
            user_data = {
                "email": fake.email(),
                "password": fake.password(length=10),
                "batch_id": batch_id,
            }
            logger.info(f"Generando usuario {i + 1}/{request.num_users}: {user_data}")
            user_response = await client.post(
                f"{settings.ALLOWED_ORIGINS}/auth/register",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            if user_response.status_code != 201:
                logger.error(f"Error al registrar usuario: {user_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al registrar usuario: {user_response.text}",
                )
            generated_users.append(user_data)
            logger.info(f"Usuario registrado con éxito: {user_data}")
            await asyncio.sleep(1.0 / request.speed_multiplier)
    logger.info(f"Generación de usuarios completada. Total: {len(generated_users)}")
    return {"msg": f"{request.num_users} usuarios registrados con éxito.", "batch_id": batch_id, "data": generated_users}


@synthetic_router.post("/posts", summary="Generar y registrar publicaciones ficticias")
async def generate_posts(
    request: PostRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    logger.info(f"Iniciando generación de publicaciones ficticias. Solicitud: {request}")
    if request.seed is not None:
        Faker.seed(request.seed)
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    new_batch = Batch(user_id=current_user.id)
    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)
    logger.info(f"Batch creado y guardado en la base de datos: {new_batch.id}")

    generated_posts = []

    async with httpx.AsyncClient() as client:
        for i in range(request.num_posts):
            post_data = {
                "title": fake.sentence(),
                "content": fake.paragraph(),
                "is_published": True,
                "user_id": request.user_id,
                "batch_id": str(new_batch.id),
            }
            logger.info(f"Generando publicación {i + 1}/{request.num_posts}: {post_data}")
            post_response = await client.post(
                f"{settings.ALLOWED_ORIGINS}/posts/create_post",
                json=post_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            if post_response.status_code != 201:
                logger.error(f"Error al crear publicación: {post_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al crear publicación: {post_response.text}",
                )
            generated_posts.append(post_data)
            logger.info(f"Publicación registrada con éxito: {post_data}")
            await asyncio.sleep(1.0 / request.speed_multiplier)

    logger.info(f"Generación de publicaciones completada. Total: {len(generated_posts)}")
    return {"msg": f"{request.num_posts} publicaciones registradas con éxito.", "batch_id": str(new_batch.id), "data": generated_posts}

@synthetic_router.post("/comments", summary="Generar y registrar comentarios ficticios")
async def generate_comments(
    request: CommentRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    logger.info(f"Iniciando generación de comentarios ficticios. Solicitud: {request}")
    if request.seed is not None:
        Faker.seed(request.seed)
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    # Crear un nuevo lote y asociarlo al usuario actual
    new_batch = Batch(user_id=current_user.id)
    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)
    logger.info(f"Batch creado y guardado en la base de datos: {new_batch.id}")

    generated_comments = []

    async with httpx.AsyncClient() as client:
        for i in range(request.num_comments):
            comment_data = {
                "content": fake.sentence(),
                "post_id": request.post_id,
                "batch_id": str(new_batch.id),
            }
            logger.info(f"Generando comentario {i + 1}/{request.num_comments}: {comment_data}")
            comment_response = await client.post(
                f"{settings.ALLOWED_ORIGINS}/interactions/{request.post_id}/comments",
                json=comment_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            if comment_response.status_code != 201:
                logger.error(f"Error al agregar comentario: {comment_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error al agregar comentario: {comment_response.text}",
                )
            generated_comments.append(comment_data)
            logger.info(f"Comentario registrado con éxito: {comment_data}")
            await asyncio.sleep(1.0 / request.speed_multiplier)
    logger.info(f"Generación de comentarios completada. Total: {len(generated_comments)}")
    return {"msg": f"{request.num_comments} comentarios registrados con éxito.", "batch_id": str(new_batch.id), "data": generated_comments}

def _assert_status(resp: httpx.Response, expected_code: int = 201) -> None:
    """Lanza una excepción si la respuesta HTTP no coincide con *expected_code*."""
    if resp.status_code != expected_code:
        raise RuntimeError(
            f"Error {resp.status_code}: {resp.text[:200]}… (expected {expected_code})"
        )

async def gen_users_ws(payload: Dict[str, Any], speed: float) -> AsyncIterator[Dict[str, Any]]:
    amount: int = payload.get("amount", 1)
    token: str = payload["token"]
    user_id: str = payload.get("user_id")
    batch_id = payload.get("batch_id") or str(uuid.uuid4())

    if "batch_id" not in payload:
        # Crear el batch en BD localmente
        async with async_session() as db:
            new_batch = Batch(id=batch_id, user_id=user_id)
            db.add(new_batch)
            await db.commit()

    async with httpx.AsyncClient(verify=False) as client:
        for _ in range(amount):
            user_data = {
                "email": fake.email(),
                "password": fake.password(length=10),
                "batch_id": batch_id,
            }
            resp = await client.post(
                f"{settings.ALLOWED_ORIGINS}auth/register",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            _assert_status(resp)
            yield user_data
            await asyncio.sleep(1.0 / speed)


async def gen_posts_ws(payload: Dict[str, Any], speed: float) -> AsyncIterator[Dict[str, Any]]:
    amount: int = payload.get("amount", 1)
    token: str = payload["token"]
    user_id: str = payload.get("user_id")
    batch_id = payload.get("batch_id") or str(uuid.uuid4())

    if "batch_id" not in payload:
        async with async_session() as db:
            new_batch = Batch(id=batch_id, user_id=user_id)
            db.add(new_batch)
            await db.commit()

    async with httpx.AsyncClient(verify=False) as client:
        for _ in range(amount):
            post_data = {
                "title": fake.sentence(),
                "content": fake.paragraph(),
                "is_published": True,
                "user_id": user_id,
                "batch_id": batch_id,
            }
            resp = await client.post(
                f"{settings.ALLOWED_ORIGINS}posts/create_post",
                json=post_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            _assert_status(resp)
            yield post_data
            await asyncio.sleep(1.0 / speed)


async def gen_comments_ws(payload: Dict[str, Any], speed: float) -> AsyncIterator[Dict[str, Any]]:
    amount: int = payload.get("amount", 1)
    token: str = payload["token"]
    user_id: str = payload.get("user_id")
    post_id: str = payload.get("post_id")
    batch_id = payload.get("batch_id") or str(uuid.uuid4())

    if "batch_id" not in payload:
        async with async_session() as db:
            new_batch = Batch(id=batch_id, user_id=user_id)
            db.add(new_batch)
            await db.commit()

    async with httpx.AsyncClient(verify=False) as client:
        for _ in range(amount):
            comment_data = {
                "content": fake.sentence(),
                "post_id": post_id,
                "batch_id": batch_id,
            }
            resp = await client.post(
                f"{settings.ALLOWED_ORIGINS}interactions/{post_id}/comments",
                json=comment_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            _assert_status(resp)
            yield comment_data
            await asyncio.sleep(1.0 / speed)
