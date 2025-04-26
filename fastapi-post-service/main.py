from fastapi import FastAPI
from app.posts.posts_routes import router
from fastapi import FastAPI
from app.db.main_db import lifespan


app = FastAPI(title="Post Microservice", lifespan=lifespan)

app.include_router(router)
