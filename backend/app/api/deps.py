from typing import Annotated
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.db.session import get_session
from app.db.redis import get_redis_pool
from app.services.turn_budget import TurnBudgetService
from app.db.models import User
from uuid import UUID

# Reusable dependencies
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[Redis, Depends(get_redis_pool)]

async def get_turn_budget_service(redis: RedisDep) -> TurnBudgetService:
    return TurnBudgetService(redis)

TurnBudgetDep = Annotated[TurnBudgetService, Depends(get_turn_budget_service)]

async def get_current_user_stub(
    x_user_id: Annotated[str | None, Header()] = None
) -> User:
    """
    Stub for authentication. 
    IN PRODUCTION: Verify JWT and fetch user.
    FOR NOW: strict B1/B3 focus, we allow passing User ID via header for testing.
    """
    if not x_user_id:
         # For testing convenience when we don't have B2 yet
        raise HTTPException(status_code=401, detail="Missing X-User-Id header (Auth stub)")
    
    # We return a mock User object with just the ID for logic checks
    # In real app, we would load from DB or JWT claims
    try:
        uid = UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid User ID format")
        
    # Mock user model for type safety in endpoints
    user = User(id=uid, phone="stub", role="user") 
    return user

CurrentUser = Annotated[User, Depends(get_current_user_stub)]
