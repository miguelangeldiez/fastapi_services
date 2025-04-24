from fastapi import Depends,APIRouter
from app.users.dependencies import current_active_user
from app.db.user import User


token_router = APIRouter()

# Ruta protegida
@token_router.get("/protected-route", tags=["users"])
def protected(user: User = Depends(current_active_user)):
    return {"message": f"Hola {user.email}, estás autenticado."}
