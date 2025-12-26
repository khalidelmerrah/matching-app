from uuid import UUID
from typing import Optional
from sqlmodel import Field, Relationship
from sqlalchemy import UniqueConstraint
from app.models.base import UUIDModel, TimestampModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.thread import Thread

class Message(UUIDModel, TimestampModel, table=True):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("thread_id", "idempotency_key", name="uix_thread_idempotency"),
    )

    thread_id: UUID = Field(foreign_key="threads.id", index=True, nullable=False)
    sender_id: UUID = Field(foreign_key="users.id", nullable=False)
    
    content: str = Field(nullable=False)
    idempotency_key: str = Field(index=True, nullable=False)
    
    media_url: Optional[str] = Field(default=None) # For future media attachment
    
    thread: "Thread" = Relationship(back_populates="messages")
