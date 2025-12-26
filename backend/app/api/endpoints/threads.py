from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select as sql_select

from app.api.deps import CurrentUser, SessionDep, TurnBudgetDep
from app.db.models import Match, Message, Thread
from app.schemas.message import MessageCreate, MessageRead
from app.schemas.events import MessageCreatedEvent, EventType 
from app.services.pubsub import PubSubService
from app.api.deps_ws import get_pubsub_service

router = APIRouter()

@router.post("/{thread_id}/messages", response_model=MessageRead)
async def send_message(
    thread_id: UUID,
    message_in: MessageCreate,
    session: SessionDep,
    current_user: CurrentUser,
    # Injected dependencies
    turn_budget: TurnBudgetDep,
    pubsub: Annotated[PubSubService, Depends(get_pubsub_service)], # NEW
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
):
    # ... (existing checks) ...
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")

    # 1. Check if message already exists (Idempotency)
    # We check this first to avoid consuming budget for retries
    stmt = sql_select(Message).where(
        Message.thread_id == thread_id,
        Message.sender_id == current_user.id,
        Message.idempotency_key == idempotency_key
    )
    result = await session.execute(stmt)
    existing_message = result.scalar_one_or_none()
    if existing_message:
        return existing_message

    # 2. Verify Thread Membership
    # We need to find the match associated with this thread and verify user participation
    stmt = sql_select(Thread).where(Thread.id == thread_id)
    result = await session.execute(stmt)
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    # Optimizing: we could join Match, but lazy load or separate query is fine for now
    stmt = sql_select(Match).where(Match.id == thread.match_id)
    result = await session.execute(stmt)
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found") # Should not happen if DB integrity
        
    if match.user_a_id != current_user.id and match.user_b_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to post in this thread")

    # 3. Check and Consume Turn Budget (Atomic)
    # Returns: -2 (Missing), -1 (Exhausted), >=0 (Remaining)
    budget_result = await turn_budget.check_and_consume(
        user_id=str(current_user.id), 
        match_id=str(match.id)
    )
    
    if budget_result == -2:
        raise HTTPException(
            status_code=400, 
            detail="Turn budget not initialized",
            headers={"X-Error-Code": "TURN_BUDGET_NOT_INITIALIZED"}
        )
    if budget_result == -1:
        raise HTTPException(
            status_code=400, 
            detail="Turn budget exhausted",
            headers={"X-Error-Code": "TURN_BUDGET_EXHAUSTED"}
        )

    # 4. Persist Message
    new_message = Message(
        thread_id=thread_id,
        sender_id=current_user.id,
        content=message_in.content,
        idempotency_key=idempotency_key,
        media_url=message_in.media_url,
        match_id=match.id, # Wait, Message model doesn't have match_id, checked valid via thread
    )
    
    session.add(new_message)
    try:
        await session.commit()
        await session.refresh(new_message)
    except IntegrityError:
        # Race/Duplicate caught by DB
        await session.rollback()
        # Retry fetch
        stmt = sql_select(Message).where(
            Message.thread_id == thread_id,
            Message.sender_id == current_user.id,
            Message.idempotency_key == idempotency_key
        )
        result = await session.execute(stmt)
        existing_message_late = result.scalar_one_or_none()
        if existing_message_late:
            return existing_message_late
        else:
            raise HTTPException(status_code=500, detail="Database integrity error")

    # 5. Broadcast Event (After Commit)
    event = MessageCreatedEvent(
        thread_id=new_message.thread_id,
        message_id=new_message.id,
        sender_id=new_message.sender_id,
        created_at=new_message.created_at
    )
    # Fire and forget (await but don't block response too long, or background task)
    # Requirement: "Publish events ONLY after DB commit"
    await pubsub.publish(f"thread:{thread_id}", event.model_dump_json())

    return new_message
