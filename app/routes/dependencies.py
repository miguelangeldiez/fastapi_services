from typing import AsyncGenerator
from uuid import UUID
from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main_db import get_db_session
from app.db.models import User
from app.config import settings

class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """
    UserManager personalizado para FastAPI Users.
    Define los secretos para reset y verificación de tokens.
    """
    reset_password_token_secret = settings.JWT_SECRET_KEY
    verification_token_secret = settings.JWT_SECRET_KEY

async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[User, UUID], None]:
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


