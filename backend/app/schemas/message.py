from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    media_url: Optional[str] = None

class MessageRead(BaseModel):
    id: UUID
    thread_id: UUID
    sender_id: UUID
    content: str
    media_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TurnBudgetError(BaseModel):
    detail: str
    code: str
