from uuid import UUID
from typing import Any
from sqlmodel import Field, Relationship, Column
from pgvector.sqlalchemy import Vector
from app.models.base import UUIDModel, TimestampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class UserEmbedding(UUIDModel, TimestampModel, table=True):
    __tablename__ = "user_embeddings"

    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True, nullable=False)
    
    # 1536 dim is standard for OpenAI text-embedding-3-small/large/ada-002
    embedding: Any = Field(sa_column=Column(Vector(1536)))

    user: "User" = Relationship(back_populates="embeddings")
