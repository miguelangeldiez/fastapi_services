from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID
import uuid
from fastapi_users import BaseUserManager, UUIDIDMixin
from pydantic import BaseModel
from app.config import get_settings
from app.db.post import User
from pydantic import BaseModel,Field
from pydantic.generics import GenericModel

T = TypeVar("T")


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
    
    user_id: UUID       = Field(..., alias="author_id")
    timestamp: datetime = Field(..., alias="created_at")
    updated_at: datetime
    class Config:
        from_attributes = True
        allow_population_by_field_name = True


class CommentOut(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    post_id: UUID
    timestamp: datetime

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


class MessageResponse(GenericModel, Generic[T]):
    msg: str
    data: Optional[T] = None

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = get_settings().JWT_SECRET_KEY
    verification_token_secret = get_settings().JWT_SECRET_KEY