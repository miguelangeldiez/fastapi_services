from typing import Any, AsyncIterator, Dict
from fastapi import APIRouter, HTTPException, status, Depends
import httpx
import asyncio
import uuid

from app.routes.schemas import CommentRequest, PostRequest, UserRequest
from app.routes.auth_routes import current_active_user
from app.db.models import Batch, User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.main_db import get_db_session, async_session
from app.routes import fake, get_token_from_cookie
from app.config import settings, logger

synthetic_router = APIRouter(prefix="/synthetic", tags=["Synthetic Data Generation"])

def _get_origin_url() -> str:
    """Devuelve el primer origen permitido para construir URLs."""
    if isinstance(settings.ALLOWED_ORIGINS, list):
        return settings.ALLOWED_ORIGINS[0]
    return settings.ALLOWED_ORIGINS

def _safe_sleep(speed: float):
    """Evita sleeps demasiado pequeños."""
    return max(0.01, 1.0 / speed)

async def _create_batch(db: AsyncSession, user_id: str) -> str:
    """Crea un nuevo batch y lo guarda en la base de datos."""
    batch_id = str(uuid.uuid4())
    new_batch = Batch(id=batch_id, user_id=user_id)
    db.add(new_batch)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Error al crear el batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el batch: {e}",
        )
    return batch_id

@synthetic_router.post("/users", summary="Generar y registrar usuarios ficticios")
async def generate_users(
    request: UserRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Genera usuarios ficticios y los registra mediante llamadas HTTP.
    """
    if request.seed is not None:
        fake.seed_instance(request.seed)
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = await _create_batch(db, current_user.id)
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_users = []
    origin_url = _get_origin_url()

    async with httpx.AsyncClient() as client:
        for i in range(request.num_users):
            user_data = {
                "email": fake.email(),
                "password": fake.password(length=10),
                "batch_id": batch_id,
            }
            logger.info(f"Generando usuario {i + 1}/{request.num_users}: {user_data}")
            user_response = await client.post(
                f"{origin_url}/auth/register",
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
            await asyncio.sleep(_safe_sleep(request.speed_multiplier))
    logger.info(f"Generación de usuarios completada. Total: {len(generated_users)}")
    return {"msg": f"{request.num_users} usuarios registrados con éxito.", "batch_id": batch_id, "data": generated_users}

@synthetic_router.post("/posts", summary="Generar y registrar publicaciones ficticias")
async def generate_posts(
    request: PostRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Genera publicaciones ficticias y las registra mediante llamadas HTTP.
    """
    if request.seed is not None:
        fake.seed_instance(request.seed)
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = await _create_batch(db, current_user.id)
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_posts = []
    origin_url = _get_origin_url()

    async with httpx.AsyncClient() as client:
        for i in range(request.num_posts):
            post_data = {
                "title": fake.sentence(),
                "content": fake.paragraph(),
                "is_published": True,
                "user_id": request.user_id,
                "batch_id": batch_id,
            }
            logger.info(f"Generando publicación {i + 1}/{request.num_posts}: {post_data}")
            post_response = await client.post(
                f"{origin_url}/posts/create_post",
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
            await asyncio.sleep(_safe_sleep(request.speed_multiplier))

    logger.info(f"Generación de publicaciones completada. Total: {len(generated_posts)}")
    return {"msg": f"{request.num_posts} publicaciones registradas con éxito.", "batch_id": batch_id, "data": generated_posts}

@synthetic_router.post("/comments", summary="Generar y registrar comentarios ficticios")
async def generate_comments(
    request: CommentRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Genera comentarios ficticios y los registra mediante llamadas HTTP.
    """
    if request.seed is not None:
        fake.seed_instance(request.seed)
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = await _create_batch(db, current_user.id)
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_comments = []
    origin_url = _get_origin_url()

    async with httpx.AsyncClient() as client:
        for i in range(request.num_comments):
            comment_data = {
                "content": fake.sentence(),
                "post_id": request.post_id,
                "batch_id": batch_id,
            }
            logger.info(f"Generando comentario {i + 1}/{request.num_comments}: {comment_data}")
            comment_response = await client.post(
                f"{origin_url}/interactions/{request.post_id}/comments",
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
            await asyncio.sleep(_safe_sleep(request.speed_multiplier))
    logger.info(f"Generación de comentarios completada. Total: {len(generated_comments)}")
    return {"msg": f"{request.num_comments} comentarios registrados con éxito.", "batch_id": batch_id, "data": generated_comments}

def _assert_status(resp: httpx.Response, expected_code: int = 201) -> None:
    """Lanza una excepción si la respuesta HTTP no coincide con *expected_code*."""
    if resp.status_code != expected_code:
        raise RuntimeError(
            f"Error {resp.status_code}: {resp.text[:200]}… (expected {expected_code})"
        )

async def gen_users_ws(payload: Dict[str, Any], speed: float) -> AsyncIterator[Dict[str, Any]]:
    """
    Generador asíncrono de usuarios ficticios para WebSocket.
    """
    amount: int = payload.get("amount", 1)
    token: str = payload["token"]
    user_id: str = payload.get("user_id")
    batch_id = payload.get("batch_id") or str(uuid.uuid4())

    if "batch_id" not in payload:
        async with async_session() as db:
            new_batch = Batch(id=batch_id, user_id=user_id)
            db.add(new_batch)
            await db.commit()

    origin_url = _get_origin_url()
    for _ in range(amount):
        user_data = {
            "email": fake.email(),
            "password": fake.password(length=10),
            "batch_id": batch_id,
        }
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(
                f"{origin_url}/auth/register",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"},
            )
        _assert_status(resp)
        yield user_data
        await asyncio.sleep(_safe_sleep(speed))

async def gen_posts_ws(payload: Dict[str, Any], speed: float) -> AsyncIterator[Dict[str, Any]]:
    """
    Generador asíncrono de publicaciones ficticias para WebSocket.
    """
    amount: int = payload.get("amount", 1)
    token: str = payload["token"]
    user_id: str = payload.get("user_id")
    batch_id = payload.get("batch_id") or str(uuid.uuid4())

    if "batch_id" not in payload:
        async with async_session() as db:
            new_batch = Batch(id=batch_id, user_id=user_id)
            db.add(new_batch)
            await db.commit()

    origin_url = _get_origin_url()
    for _ in range(amount):
        post_data = {
            "title": fake.sentence(),
            "content": fake.paragraph(),
            "is_published": True,
            "user_id": user_id,
            "batch_id": batch_id,
        }
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(
                f"{origin_url}/posts/create_post",
                json=post_data,
                headers={"Authorization": f"Bearer {token}"},
            )
        _assert_status(resp)
        yield post_data
        await asyncio.sleep(_safe_sleep(speed))

async def gen_comments_ws(payload: Dict[str, Any], speed: float) -> AsyncIterator[Dict[str, Any]]:
    """
    Generador asíncrono de comentarios ficticios para WebSocket.
    """
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

    origin_url = _get_origin_url()
    for _ in range(amount):
        comment_data = {
            "content": fake.sentence(),
            "post_id": post_id,
            "batch_id": batch_id,
        }
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(
                f"{origin_url}/interactions/{post_id}/comments",
                json=comment_data,
                headers={"Authorization": f"Bearer {token}"},
            )
        _assert_status(resp)
        yield comment_data
        await asyncio.sleep(_safe_sleep(speed))
