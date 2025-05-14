from enum import Enum
from pydantic import BaseModel, Field, confloat
from typing import Any, Dict, Optional

from pydantic import BaseModel
from typing import Optional

class BaseRequest(BaseModel):
    seed: Optional[int] = None  # Semilla opcional proporcionada por el cliente
    speed_multiplier: float = 1.0  # Velocidad de generación
    mode: str = "pull"  # pull (respuesta directa) o push (WebSocket)

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

class WSRequest(BaseModel):
    action: Action
    payload: Dict[str, Any] = Field(default_factory=dict)
    speed_multiplier: confloat = Field(1.0, gt=0, le=100)  # evita división por 0
