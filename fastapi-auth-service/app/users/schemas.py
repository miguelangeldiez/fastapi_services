import uuid
from fastapi_users import schemas,BaseUserManager, UUIDIDMixin
from pydantic import BaseModel
from config import get_settings
from app.db.user_model import User

class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str | None

class UserCreate(schemas.BaseUserCreate):
    username: str | None

class Token(BaseModel):
    token: str

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = get_settings().JWT_SECRET_KEY
    verification_token_secret = get_settings().JWT_SECRET_KEY