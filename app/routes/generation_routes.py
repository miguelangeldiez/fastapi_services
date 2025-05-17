from fastapi import APIRouter, Depends
import asyncio

from app.routes.schemas import CommentRequest, PostRequest, UserRequest
from app.services.auth_service import current_active_user, get_token_from_cookie, get_user_manager
from app.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.main_db import get_db_session
from app.config import logger
from app.services.synthetic_service import create_batch, create_fake_user, create_fake_post, create_fake_comment, set_fake_seed
from sqlalchemy.exc import IntegrityError

synthetic_router = APIRouter(prefix="/synthetic", tags=["Synthetic Data Generation"])

def _safe_sleep(speed: float):
    """Evita sleeps demasiado pequeños."""
    return max(0.01, 1.0 / speed)

@synthetic_router.post("/users", summary="Generar y registrar usuarios ficticios")
async def generate_users(
    request: UserRequest,
    token: str = Depends(get_token_from_cookie),
    current_user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db_session),
    user_manager = Depends(get_user_manager),
):
    """
    Genera usuarios ficticios y los registra directamente en la base de datos.
    """
    set_fake_seed(request.seed)
    if request.seed is not None:
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = await create_batch(db, current_user.id)
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_users = []
    for _ in range(request.num_users):
        user_data = await create_fake_user(db, batch_id, user_manager=user_manager)
        generated_users.append(user_data)
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
    Genera publicaciones ficticias y las registra directamente en la base de datos.
    """
    set_fake_seed(request.seed)
    if request.seed is not None:
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = await create_batch(db, current_user.id)
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_posts = []
    for _ in range(request.num_posts):
        try:
            post_data = await create_fake_post(db, request.user_id, batch_id)
        except IntegrityError as e:
            await db.rollback()
            if "foreign key constraint" in str(e).lower() or "violates foreign key" in str(e).lower():
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail=f"El user_id '{request.user_id}' no existe."
                )
            raise
        generated_posts.append(post_data)
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
    Genera comentarios ficticios y los registra directamente en la base de datos.
    """
    set_fake_seed(request.seed)
    if request.seed is not None:
        logger.info(f"Semilla establecida para Faker: {request.seed}")

    batch_id = await create_batch(db, current_user.id)
    logger.info(f"Batch creado y guardado en la base de datos: {batch_id}")

    generated_comments = []
    for _ in range(request.num_comments):
        comment_data = await create_fake_comment(db, current_user.id, request.post_id, batch_id)
        generated_comments.append(comment_data)
        await asyncio.sleep(_safe_sleep(request.speed_multiplier))
    logger.info(f"Generación de comentarios completada. Total: {len(generated_comments)}")
    return {"msg": f"{request.num_comments} comentarios registrados con éxito.", "batch_id": batch_id, "data": generated_comments}
