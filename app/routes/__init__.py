from faker import Faker
from fastapi import HTTPException, Request, status

fake = Faker()

# Función para extraer el token de la cookie
def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("threadfit_cookie")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no encontrado en las cookies.",
        )
    return token