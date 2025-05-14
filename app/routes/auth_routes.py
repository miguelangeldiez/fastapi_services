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
from config import get_settings

# Initialize settings
settings = get_settings()

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.JWT_SECRET_KEY,
        lifetime_seconds=settings.JWT_LIFETIME_SECONDS,
    )

# --- Configuración de autenticación JWT vía cookie ---

# 1) Definimos el transporte que usará cookies
cookie_transport = CookieTransport(
    cookie_name=settings.COOKIE_NAME,
    cookie_max_age=settings.JWT_LIFETIME_SECONDS,
    cookie_secure=True,  
    cookie_httponly=True  
)  # :contentReference[oaicite:4]{index=4}

# 2) Backend de autenticación
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)  # :contentReference[oaicite:6]{index=6}

# 4) Instanciamos FastAPIUsers
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# 5) Dependencia para obtener el usuario activo
current_active_user = fastapi_users.current_user(active=True)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
# Login JWT
auth_router.include_router(fastapi_users.get_auth_router(auth_backend))

# Registro de usuarios
auth_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))

