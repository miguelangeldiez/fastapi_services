from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID
from fastapi_users import BaseUserManager, UUIDIDMixin,schemas
from pydantic import BaseModel
from config import get_settings
from app.db.models import User

T = TypeVar("T")
class UserRead(schemas.BaseUser[UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    batch_id: Optional[UUID] = None  # Incluir el campo batch_id


class Token(BaseModel):
    pass


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = get_settings().JWT_SECRET_KEY
    verification_token_secret = get_settings().JWT_SECRET_KEY


class PostCreate(BaseModel):
    title: str
    content: str
    is_published: bool = False

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    id: UUID
    content: str
    is_published: bool
    
    user_id: UUID       
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
        allow_population_by_field_name = True

class CommentCreate(BaseModel):
    content: str

    class Config:
        from_attributes = True

class CommentOut(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    post_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedPostsResponse(BaseModel):
    posts: List[PostOut]
    total: int
    pages: int
    current_page: int
    per_page: int
    has_next: bool
    has_prev: bool


class MessageResponse(BaseModel, Generic[T]):
    msg: str
    data: Optional[T] = None

class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = get_settings().JWT_SECRET_KEY
    verification_token_secret = get_settings().JWT_SECRET_KEY