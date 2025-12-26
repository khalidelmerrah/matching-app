from enum import Enum
from uuid import UUID
from typing import List
from sqlmodel import Field, Relationship
from app.models.base import UUIDModel, TimestampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.message import Message

class ThreadState(str, Enum):
    BLIND_VOLLEY = "blind_volley"  # Initial state, silhouette only
    REVEAL_1 = "reveal_1"          # Partial reveal
    REVEAL_2 = "reveal_2"          # More reveal
    FULL_REVEAL = "full_reveal"    # Full profile visible

class Thread(UUIDModel, TimestampModel, table=True):
    __tablename__ = "threads"

    match_id: UUID = Field(foreign_key="matches.id", unique=True, index=True, nullable=False)
    
    current_state: ThreadState = Field(default=ThreadState.BLIND_VOLLEY)
    turn_count: int = Field(default=0)
    reveal_level: int = Field(default=0)
    
    # Relationships
    match: "Match" = Relationship(back_populates="thread")
    messages: List["Message"] = Relationship(back_populates="thread")
