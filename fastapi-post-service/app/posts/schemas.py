from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID
import uuid
from fastapi_users import BaseUserManager, UUIDIDMixin
from pydantic import BaseModel
from app.config import get_settings
from app.db.post import User
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class PostCreate(BaseModel):
    content: str


class PostOut(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True


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