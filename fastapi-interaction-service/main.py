from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager
from contextlib import asynccontextmanager

from app.socket.events import register_socket_events
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import get_settings
from app.interactions import comments,likes

settings = get_settings()

engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False,class_=AsyncSession)
Base = declarative_base()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    
app = FastAPI(title="Interaction Microservice",lifespan=lifespan)

# Middleware CORS para HTTP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8000"],  # o ["*"] si solo testear
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(comments.router,prefix="/posts,tags=["Comments"])
app.include_router(likes.router,prefix="/posts,tags=["Likes"])
app.include_router(websocket_router,tags=["WebScoket"])

