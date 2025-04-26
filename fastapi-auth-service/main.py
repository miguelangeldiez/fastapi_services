from fastapi import FastAPI
from app.users.dependencies import fastapi_users, auth_backend
from app.users.schemas import UserRead, UserCreate
from app.db.main_db import engine, Base, lifespan

app = FastAPI(title="Auth Microservice", lifespan=lifespan)

# Login JWT
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

# Registro de usuarios
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
