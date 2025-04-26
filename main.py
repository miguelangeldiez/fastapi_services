from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import posts_router, interactions_router, auth_router, profile_router

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="ThreadFit",
    description="Microservicio para gestionar publicaciones, interacciones, autenticación y perfiles.",
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
app.include_router(posts_router)
app.include_router(auth_router)
app.include_router(interactions_router)
app.include_router(profile_router)

# Punto de inicio
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bienvenido a ThreadFit API"}