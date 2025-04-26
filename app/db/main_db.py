
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config import get_settings

settings = get_settings()

engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False,class_=AsyncSession)
Base = declarative_base()

