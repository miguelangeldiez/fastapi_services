# users/dependencies.py

from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.authentication import (
    JWTStrategy,
)

from app.db.main_db import async_session, get_db_session
from app.db.models import User
from .schemas import UserManager
from config import get_settings

settings = get_settings()



async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    Crea el adaptador de FastAPI Users para SQLAlchemy.
    """
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """
    Instancia el UserManager personalizado.
    """
    yield UserManager(user_db)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.JWT_LIFETIME_SECONDS,
    )


