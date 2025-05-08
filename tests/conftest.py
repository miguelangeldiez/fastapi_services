import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.main_db import get_db_session, Base, engine

@pytest.fixture(scope="function", autouse=True)
async def clean_database():
    async with engine.begin() as conn:
        # Elimina y recrea todas las tablas
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield