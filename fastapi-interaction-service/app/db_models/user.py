
from sqlalchemy.orm import Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from ...main import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(nullable=True, unique=True)
