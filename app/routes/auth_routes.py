from fastapi import APIRouter, Depends
from .dependencies import fastapi_users      

from app.routes.schemas import UserCreate, UserRead
from .dependencies import auth_backend, current_active_user


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
# Login JWT
auth_router.include_router(fastapi_users.get_auth_router(auth_backend))

# Registro de usuarios
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
