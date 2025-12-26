from typing import Annotated
from uuid import UUID
from fastapi import Depends, Query, WebSocket, status
from redis.asyncio import Redis
from app.db.redis import get_redis_pool
from app.services.pubsub import PubSubService

async def get_pubsub_service(redis: Annotated[Redis, Depends(get_redis_pool)]) -> PubSubService:
    return PubSubService(redis)

async def get_current_user_ws(
    websocket: WebSocket,
    user_id: Annotated[str | None, Query()] = None
) -> str | None:
    """
    Stub for WebSocket auth. Reads user_id from query param.
    """
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    
    try:
        UUID(user_id)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
        
    return user_id

PubSubDep = Annotated[PubSubService, Depends(get_pubsub_service)]
