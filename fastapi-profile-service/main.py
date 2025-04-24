from fastapi import FastAPI, Depends
from app.users.dependencies import fastapi_users, auth_backend, current_active_user
from app.users.schemas import UserRead, UserCreate
from app.db_models.user import User
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.init_db import init_db



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
app = FastAPI(title="Auth Microservice",lifespan=lifespan)

# Login JWT
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

# Registro de usuarios
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# Ruta protegida
@app.get("/protected-route", tags=["users"])
def protected(user: User = Depends(current_active_user)):
    return {"message": f"Hola {user.email}, estás autenticado."}
