from fastapi import APIRouter
from app.routes.dependencies import get_user_manager
from app.routes.schemas import UserCreate, UserRead
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    CookieTransport,
    AuthenticationBackend,
    JWTStrategy,
)
import uuid
from app.db.models import User
from app.config import settings

# --- Configuración de autenticación JWT vía cookie ---

def get_jwt_strategy() -> JWTStrategy:
    """
    Retorna la estrategia JWT configurada con los parámetros del entorno.
    """
    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.JWT_LIFETIME_SECONDS,
    )

# 1) Definir el transporte de autenticación por cookie
cookie_transport = CookieTransport(
    cookie_name=settings.COOKIE_NAME,
    cookie_max_age=settings.JWT_LIFETIME_SECONDS,
    cookie_secure=True,      # Solo enviar la cookie por HTTPS
    cookie_httponly=True     # No accesible desde JavaScript
)

# 2) Configurar el backend de autenticación
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

# 3) Instanciar FastAPIUsers con el UserManager y el backend configurado
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# 4) Dependencia para obtener el usuario activo autenticado
current_active_user = fastapi_users.current_user(active=True)

# 5) Definir el router de autenticación
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# 6) Incluir rutas de autenticación y registro de usuarios
auth_router.include_router(fastapi_users.get_auth_router(auth_backend))
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))

