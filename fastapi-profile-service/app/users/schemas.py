import uuid
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str | None

class UserCreate(schemas.BaseUserCreate):
    username: str | None
