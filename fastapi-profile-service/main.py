from fastapi import FastAPI
from app.profile.profile_routes import router
from fastapi import FastAPI
from app.db.main_db import lifespan


app = FastAPI(title="Profile Microservice", lifespan=lifespan)

app.include_router(router)
