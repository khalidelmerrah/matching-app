from enum import Enum
from uuid import UUID
from typing import Optional
from sqlmodel import Field, Relationship
from app.models.base import UUIDModel, TimestampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.thread import Thread

class MatchStatus(str, Enum):
    active = "active"
    unmatched = "unmatched"
    archived = "archived"

class Match(UUIDModel, TimestampModel, table=True):
    __tablename__ = "matches"

    user_a_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    user_b_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    
    score: float = Field(default=0.0)
    status: MatchStatus = Field(default=MatchStatus.active)
    
    # Relationships
    thread: Optional["Thread"] = Relationship(back_populates="match", sa_relationship_kwargs={"uselist": False})
