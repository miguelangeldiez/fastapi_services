from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    num_users: int = 10
    seed: Optional[int] = None  # Semilla opcional proporcionada por el cliente
    speed_multiplier: float = 1.0  # Velocidad de generación

class PostRequest(BaseModel):
    num_posts: int = 10
    user_id: str
    seed: Optional[int] = None  # Semilla opcional proporcionada por el cliente
    speed_multiplier: float = 1.0  # Velocidad de generación

class CommentRequest(BaseModel):
    num_comments: int = 10
    post_id: str
    seed: Optional[int] = None  # Semilla opcional proporcionada por el cliente
    speed_multiplier: float = 1.0  # Velocidad de generación

class LikeRequest(BaseModel):
    num_likes: int = 10
    post_id: str
    seed: Optional[int] = None  # Semilla opcional proporcionada por el cliente
    speed_multiplier: float = 1.0  # Velocidad de generación