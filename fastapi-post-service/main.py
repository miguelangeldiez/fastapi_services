from fastapi import FastAPI
from app.posts.posts import router
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.main_db import engine,Base



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    
app = FastAPI(title="Post Microservice",lifespan=lifespan)

app.include_router(router)
