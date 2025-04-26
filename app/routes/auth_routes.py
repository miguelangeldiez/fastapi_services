from fastapi import APIRouter, Depends
import fastapi_users

from app.routes.schemas import UserCreate, UserRead
from config import auth_backend,current_active_user


auth_router = APIRouter(
    prefix="/posts", tags=["posts"], dependencies=[Depends(current_active_user)]
)
# Login JWT
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

# Registro de usuarios
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
