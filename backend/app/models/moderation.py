from uuid import UUID
from typing import Optional
from sqlmodel import Field
from app.models.base import UUIDModel, TimestampModel

class Block(UUIDModel, TimestampModel, table=True):
    __tablename__ = "blocks"

    blocker_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    blocked_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    reason: Optional[str] = Field(default=None)

class Report(UUIDModel, TimestampModel, table=True):
    __tablename__ = "reports"

    reporter_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    reported_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    reason: str = Field(nullable=False)
    details: Optional[str] = Field(default=None)
