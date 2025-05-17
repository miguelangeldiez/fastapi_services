import uuid
from app.db.models import Batch, User, Post, Comment
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.services.auth_service import get_password_hash, get_user_manager
from app.routes.schemas import UserCreate

from faker import Faker

fake = Faker()

def set_fake_seed(seed: int | None):
    if seed is not None:
        fake.seed_instance(seed)

async def create_batch(db: AsyncSession, user_id: str) -> str:
    batch_id = str(uuid.uuid4())
    new_batch = Batch(id=batch_id, user_id=user_id)
    db.add(new_batch)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el batch: {e}",
        )
    return batch_id

async def create_fake_user(
    db: AsyncSession,
    batch_id: str,
    user_manager=None,
) -> dict:
    user_data = {
        "email": fake.email(),
        "password": fake.password(length=10),
        "batch_id": batch_id,
    }
    # Si no se pasa un user_manager, lo obtenemos (esto requiere contexto de FastAPI)
    if user_manager is None:
        # Esto solo funciona dentro de una request FastAPI
        async for um in get_user_manager():
            user_manager = um
            break

    # Usar el método de FastAPI Users para crear el usuario
    user_create = UserCreate(**user_data)
    try:
        user = await user_manager.create(user_create, safe=True, request=None)
    except Exception as e:
        raise RuntimeError(f"Error al crear usuario con FastAPI Users: {e}")

    return {
        "id": str(user.id),
        "email": user.email,
        "batch_id": str(batch_id),
        "password": user_data["password"],  
    }

async def create_fake_post(db: AsyncSession, user_id: str, batch_id: str) -> dict:
    post_data = {
        "title": fake.sentence(),
        "content": fake.paragraph(),
        "is_published": True,
        "user_id": user_id,
        "batch_id": batch_id,
    }
    new_post = Post(**post_data)
    db.add(new_post)
    try:
        await db.commit()
        await db.refresh(new_post)
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"Error al crear publicación: {e}")
    return {
        "id": str(new_post.id),
        "title": new_post.title,
        "content": new_post.content,
        "batch_id": str(new_post.batch_id),
    }

async def create_fake_comment(db: AsyncSession, user_id: str, post_id: str, batch_id: str) -> dict:
    comment_data = {
        "content": fake.sentence(),
        "post_id": post_id,
        "batch_id": batch_id,
        "user_id": user_id,
    }
    new_comment = Comment(**comment_data)
    db.add(new_comment)
    try:
        await db.commit()
        await db.refresh(new_comment)
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"Error al crear comentario: {e}")
    return {
        "id": str(new_comment.id),
        "content": new_comment.content,
        "post_id": str(new_comment.post_id),
        "batch_id": str(new_comment.batch_id),
        "user_id": str(new_comment.user_id),
    }