"""
Inicialización de la base de datos y sesión asíncrona para SQLAlchemy.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import get_settings, logger

settings = get_settings()

# Permite configurar el log de SQL por variable de entorno
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=getattr(settings, "DB_ECHO", False),
    future=True,
)

# Sessionmaker asíncrono para SQLAlchemy
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Declarative base para los modelos ORM
Base = declarative_base()

__all__ = ["engine", "async_session", "Base", "get_db_session"]

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Proporciona una sesión asíncrona de base de datos para inyección de dependencias.
    """
    logger.debug("Creando una nueva sesión de base de datos.")
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.exception("Error en la sesión de base de datos", exc_info=True)
            raise
        finally:
            logger.debug("Cerrando la sesión de base de datos.")