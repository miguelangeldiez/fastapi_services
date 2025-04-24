# users/dependencies.py

from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users.authentication import (
    CookieTransport,
    AuthenticationBackend,
    JWTStrategy,
)
import uuid

from ...main import async_session
from ..db_models.user import User
from .manager import UserManager
from ..config import get_settings

settings = get_settings()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Crea y cierra correctamente la sesión de SQLAlchemy.
    """
    async with async_session() as session:
        yield session


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


# --- Configuración de autenticación JWT vía cookie ---

# 1) Definimos el transporte que usará cookies
cookie_transport = CookieTransport(
    cookie_name="threadfit_cookie",
    cookie_max_age=3600,  # 1 hora
)  # :contentReference[oaicite:4]{index=4}

# 2) Estrategia JWT
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.JWT_LIFETIME_SECONDS,
    )  # :contentReference[oaicite:5]{index=5}

# 3) Backend de autenticación
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)  # :contentReference[oaicite:6]{index=6}

# 4) Instanciamos FastAPIUsers
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# 5) Dependencia para obtener el usuario activo
current_active_user = fastapi_users.current_user(active=True)
