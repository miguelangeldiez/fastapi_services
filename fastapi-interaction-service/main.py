from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.main_db import lifespan
from app.interactions import interactions_router
    
app = FastAPI(title="Interaction Microservice",lifespan=lifespan)

# Middleware CORS para HTTP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8000"],  # o ["*"] si solo testear
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interactions_router, prefix="/posts", tags=["Comments"])