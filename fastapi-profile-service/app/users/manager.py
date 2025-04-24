import uuid
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.db_models.user import User
from ..config import get_settings

settings = get_settings()

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.JWT_SECRET_KEY
    verification_token_secret = settings.JWT_SECRET_KEY
