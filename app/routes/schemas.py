from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID
from fastapi_users import BaseUserManager, UUIDIDMixin, schemas
from pydantic import BaseModel, ConfigDict
from app.db.models import User
from config import get_settings

T = TypeVar("T")


class UserRead(schemas.BaseUser[UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    batch_id: Optional[UUID] = None  # Permitir que se pase batch_id opcionalmente
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,   # so that if you ever alias fields, Pydantic will let you use the name
    )


class Token(BaseModel):
    pass


class UserManager(UUIDIDMixin, BaseUserManager["User", UUID]):  # Usa una referencia de cadena para evitar el ciclo
    reset_password_token_secret = get_settings().JWT_SECRET_KEY
    verification_token_secret = get_settings().JWT_SECRET_KEY

   


class PostCreate(BaseModel):
    title: str
    content: str
    is_published: bool = False

    model_config = ConfigDict(from_attributes=True)


class PostOut(BaseModel):
    id: UUID
    title: str
    content: str
    is_published: bool
    
    user_id: UUID       
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True,allow_population_by_field_name = True)
        

class CommentCreate(BaseModel):
    content: str

    model_config = ConfigDict(from_attributes=True)

class CommentOut(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    post_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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