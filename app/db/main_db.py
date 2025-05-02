
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config import get_settings

settings = get_settings()

engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False,class_=AsyncSession)
Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Crea y cierra correctamente la sesión de SQLAlchemy.
    """
    async with async_session() as session:
        yield session