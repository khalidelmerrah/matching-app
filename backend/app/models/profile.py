from typing import Any, Dict, Optional
from uuid import UUID
from sqlmodel import Field, Relationship, Column
from sqlalchemy import JSON
from app.models.base import UUIDModel, TimestampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class UserProfile(UUIDModel, TimestampModel, table=True):
    __tablename__ = "user_profiles"

    user_id: UUID = Field(foreign_key="users.id", unique=True, index=True, nullable=False)
    
    name: str = Field(nullable=False)
    bio: Optional[str] = Field(default=None)
    birthdate: Optional[str] = Field(default=None) # Keep as ISO string or use date
    location: Optional[str] = Field(default=None) # Placeholder
    gender: Optional[str] = Field(default=None)
    
    preferences: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    user: "User" = Relationship(back_populates="profile")
