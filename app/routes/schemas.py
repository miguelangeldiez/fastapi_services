from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID
from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class UserRead(schemas.BaseUser[UUID]):
    """Datos públicos del usuario autenticado."""
    pass

class UserCreate(schemas.BaseUserCreate):
    """Datos requeridos para crear un usuario."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class PostCreate(BaseModel):
    """Datos para crear un post."""
    title: str
    content: str
    is_published: bool = False

    model_config = ConfigDict(from_attributes=True)

class PostOut(BaseModel):
    """Datos de salida de un post."""
    id: UUID
    title: str
    content: str
    is_published: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

class CommentCreate(BaseModel):
    """Datos para crear un comentario."""
    content: str

    model_config = ConfigDict(from_attributes=True)

class CommentOut(BaseModel):
    """Datos de salida de un comentario."""
    id: UUID
    content: str
    user_id: UUID
    post_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedPostsResponse(BaseModel):
    """Respuesta paginada de posts."""
    posts: List[PostOut]
    total: int
    pages: int
    current_page: int
    per_page: int
    has_next: bool
    has_prev: bool

class MessageResponse(BaseModel, Generic[T]):
    """Respuesta estándar con mensaje y datos opcionales."""
    msg: str
    data: Optional[T] = None

class BaseRequest(BaseModel):
    """Base para requests de generación sintética."""
    seed: Optional[int] = None
    speed_multiplier: float = 1.0

class UserRequest(BaseRequest):
    num_users: int = 10

class PostRequest(BaseRequest):
    num_posts: int = 10
    user_id: str

class CommentRequest(BaseRequest):
    num_comments: int = 10
    post_id: str

class LikeRequest(BaseRequest):
    num_likes: int = 10
    post_id: str

# --- Pydantic Models para WebSocket ---
class Action(str, Enum):
    generate_users = "generate_users"
    generate_posts = "generate_posts"
    generate_comments = "generate_comments"

class WSMessage(BaseModel):
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    speed_multiplier: float = Field(1.0, ge=0.1, le=20)
