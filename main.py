from fastapi import FastAPI
from app.routes import posts_router, interactions_router, auth_router, profile_router
from fastapi import FastAPI

app = FastAPI(title="ThreadFit")

app.include_router(posts_router)
app.include_router(auth_router)
app.include_router(interactions_router)
app.include_router(profile_router)
