from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel

class EventType(str, Enum):
    MESSAGE_CREATED = "message.created"

class BaseEvent(BaseModel):
    type: EventType
    created_at: datetime = datetime.utcnow()

class MessageCreatedEvent(BaseEvent):
    type: EventType = EventType.MESSAGE_CREATED
    thread_id: UUID
    message_id: UUID
    sender_id: UUID
    # We DO NOT include content by default for privacy/security in broadcast
    # frontend will fetch details or we send only if confirmed safe
    # For now: strict B5 requirements says "Do not broadcast full message content if that creates privacy... risk"
    # We will include it for MVP as it's encrypted/safe in DB, but let's stick to metadata + maybe snippet?
    # Actually, user said: "include content only if already stored and safe per current state"
    # We will just send IDs for now to be safe and efficient. Client fetches if needed, or we assume client has it if they sent it (optimization).
    # But for the OTHER user, they need to know.
    # Let's send the content for now, assuming TLS + Auth WSS is secure enough.
    # Re-reading: "Broadcast payload: message.created { thread_id, message_id, sender_id, type, created_at }"
    # The requirement explicitly LISTS the fields. Content is NOT in the list.
    # I will strictly follow the list. 
    
    pass 
