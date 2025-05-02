# models.py
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from .main_db import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    batches = relationship(
        "Batch",
        back_populates="user",
        foreign_keys="Batch.user_id"  # Especifica la clave foránea
    )
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    batch = relationship(
        "Batch",
        backref="generated_users",
        foreign_keys=[batch_id]  # Especifica la clave foránea
    )

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    comments = relationship("Comment", back_populates="post")
    user = relationship("User", backref="posts")
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False,)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    batch = relationship("Batch", backref="posts")  # Relación opcional con Batch

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False,)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),nullable=False,)
    post_id = Column(UUID(as_uuid=True),ForeignKey("posts.id", ondelete="CASCADE"),nullable=False,)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True)
    batch = relationship("Batch", backref="comments")  # Relación opcional con Batch
    user = relationship("User", backref="comments")
    post = relationship("Post", back_populates="comments")

class Like(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False,)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    batch_id = Column(UUID(as_uuid=True), nullable=True)
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="unique_like_per_user_post"),)

class Batch(Base):
    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación inversa con el modelo User
    user = relationship(
        "User",
        back_populates="batches",
        foreign_keys=[user_id]  # Especifica la clave foránea
    )