from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Importación de routers de la aplicación
from app.routes.auth_routes import auth_router
from app.routes.profile_routes import profile_router
from app.routes.posts_routes import posts_router
from app.routes.interactions_routes import interactions_router
from app.routes.generation_routes import synthetic_router
from app.routes.data_collection_routes import data_router
from app.real_time.websockets_routes import websocket_router

# Configuración y logging
from app.config import logger, settings

# Inicialización de la aplicación FastAPI
app = FastAPI(
    title="ThreadFit",
    description="Servicios para gestionar publicaciones, interacciones, autenticación y perfiles.",
    version="1.0.0",
)

# Redirección raíz a la documentación interactiva
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Configuración del middleware CORS
# En producción, settings.ALLOWED_ORIGINS debe ser una lista de dominios permitidos
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def register_routers(app: FastAPI):
    """
    Registra todos los routers de la aplicación.
    """
    app.include_router(auth_router)
    app.include_router(profile_router)
    app.include_router(posts_router)
    app.include_router(interactions_router)
    app.include_router(synthetic_router)
    app.include_router(data_router)
    app.include_router(websocket_router)

# Registro de routers
register_routers(app)
logger.info("Todos los routers han sido registrados.")

# Eventos de ciclo de vida de la aplicación
@app.on_event("startup")
async def startup_event():
    logger.info("La aplicación ThreadFit ha iniciado.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("La aplicación ThreadFit se está cerrando.")
