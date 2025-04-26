# models.py
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship,Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from .main_db import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(nullable=True, unique=True)


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    comments = relationship("Comment", back_populates="post")
    user = relationship("User", backref="posts")
    is_published = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False,)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False,)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey("user.id", ondelete="CASCADE"),nullable=False,)
    post_id = Column(UUID(as_uuid=True),ForeignKey("posts.id", ondelete="CASCADE"),nullable=False,)

    user = relationship("User", backref="comments")
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)

    __table_args__ = (UniqueConstraint("post_id", "user_id", name="unique_like_per_user_post"),)

