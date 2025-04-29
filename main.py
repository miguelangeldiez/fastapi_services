from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.interactions_routes import interactions_router
from app.routes.posts_routes import posts_router
from app.routes.profile_routes import profile_router
from app.routes.auth_routes import auth_router

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="ThreadFit",
    description="Servicios para gestionar publicaciones, interacciones, autenticación y perfiles.",
    version="1.0.0",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(posts_router)
app.include_router(interactions_router)
