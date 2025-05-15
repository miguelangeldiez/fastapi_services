from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config import get_settings, logger

settings = get_settings()

engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False,class_=AsyncSession)
Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    logger.info("Creando una nueva sesión de base de datos.")
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.exception("Error en la sesión de base de datos", exc_info=True)
            raise
        finally:
            logger.info("Cerrando la sesión de base de datos.")