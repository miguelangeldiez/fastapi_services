from fastapi import APIRouter
from app.routes.schemas import UserCreate, UserRead
from app.services.auth_service import auth_backend, fastapi_users
# Definir el router de autenticación
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Incluir rutas de autenticación y registro de usuarios
auth_router.include_router(fastapi_users.get_auth_router(auth_backend))
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))

