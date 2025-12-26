from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship
from app.models.base import UUIDModel, TimestampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.profile import UserProfile
    from app.models.embedding import UserEmbedding

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(UUIDModel, TimestampModel, table=True):
    __tablename__ = "users"

    phone: str = Field(index=True, unique=True, nullable=False)
    email: Optional[str] = Field(default=None, index=True, unique=True)
    role: UserRole = Field(default=UserRole.USER)
    
    # Relationships
    profile: Optional["UserProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    embeddings: Optional["UserEmbedding"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    
    # We will define other relationships as we implement their models to avoid circular imports 
    # or just use string forward references.
