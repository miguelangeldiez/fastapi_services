# models.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship,Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from app.db import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(nullable=True, unique=True)


class Post(Base):
    __tablename__ = "posts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True
    )
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default= datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default= datetime.now(timezone.utc),
        onupdate= datetime.now(timezone.utc),
        nullable=False
    )

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="posts")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    content = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=datetime.now(timezone.utc),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id = Column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relaciones ORM
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")