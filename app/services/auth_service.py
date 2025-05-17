from fastapi import HTTPException, Request, status, Depends
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import (
    CookieTransport,
    AuthenticationBackend,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session,User
from app.config import settings
import uuid
from typing import AsyncGenerator
from uuid import UUID

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
    """Crea el adaptador de FastAPI Users para SQLAlchemy."""
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[User, UUID] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Instancia el UserManager personalizado."""
    yield UserManager(user_db)

def get_jwt_strategy() -> JWTStrategy:
    """Retorna la estrategia JWT configurada con los parámetros del entorno."""
    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.JWT_LIFETIME_SECONDS,
    )

cookie_transport = CookieTransport(
    cookie_name=settings.COOKIE_NAME,
    cookie_max_age=settings.JWT_LIFETIME_SECONDS,
    cookie_secure=True,      # Cambia a False si necesitas pruebas locales sin HTTPS
    cookie_httponly=True
)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)

def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no encontrado en las cookies.",
        )
    return token