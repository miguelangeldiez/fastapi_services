from pydantic import BaseModel
from typing import Optional

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