import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from app.db import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Modelo de usuario para autenticación y relaciones.
    batch_id solo se asigna a usuarios ficticios creados por lote.
    """
    __tablename__ = "users"
    batches = relationship(
        "Batch",
        back_populates="user",
        foreign_keys="Batch.user_id"  # Especifica la clave foránea
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

class Post(Base):
    """
    Modelo de publicación.
    """
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

    def __repr__(self):
        return f"<Post id={self.id} title={self.title}>"

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False,)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),nullable=False,)
    post_id = Column(UUID(as_uuid=True),ForeignKey("posts.id", ondelete="CASCADE"),nullable=False,)
    user = relationship("User", backref="comments")
    post = relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"<Comment id={self.id}>"

class Like(Base):
    __tablename__ = "likes"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False,)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    batch_id = Column(UUID(as_uuid=True), nullable=True)
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="unique_like_per_user_post"),)

    def __repr__(self):
        return f"<Like id={self.id}>"

class Batch(Base):
    __tablename__ = "batches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="batches", foreign_keys=[user_id])

    def __repr__(self):
        return f"<Batch id={self.id}>"