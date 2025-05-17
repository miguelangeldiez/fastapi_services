import uuid
from app.db.models import Batch, User, Post, Comment
from sqlalchemy.ext.asyncio import AsyncSession
from app.routes import fake
from fastapi import HTTPException, status

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

async def create_fake_user(db: AsyncSession, batch_id: str) -> dict:
    user_data = {
        "email": fake.email(),
        "password": fake.password(length=10),
        "batch_id": batch_id,
    }
    new_user = User(
        email=user_data["email"],
        hashed_password=user_data["password"],  # Hash si es necesario
        batch_id=batch_id,
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise RuntimeError(f"Error al crear usuario: {e}")
    return user_data

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
    return post_data

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
    return comment_data