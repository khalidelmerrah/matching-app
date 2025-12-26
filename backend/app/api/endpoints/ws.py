import asyncio
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException
from sqlalchemy import select
from sqlmodel import select as sql_select

from app.db.session import async_session_factory
from app.db.models import Message, Thread, Match, User
from app.services.pubsub import PubSubService
from app.api.deps import get_redis_pool
from app.api.deps_ws import get_pubsub_service
from app.db.redis import get_redis_pool as get_redis_pool_dep
# We need basic auth here too. WS doesn't support headers well in standard JS API (except protocol).
# Standard practice: passing token in query param for WS or cookie.
# For B5, we'll assume query param ?token=... for MVP or strictly header if client supports.
# Let's use a query param `x_user_id` stub for now consistent with HTTP.

router = APIRouter()

@router.websocket("/ws/threads/{thread_id}")
async def websocket_thread_stream(
    websocket: WebSocket,
    thread_id: UUID,
    # Injected dependencies
    redis=Depends(get_redis_pool_dep),
    # Note: Depends in WebSocket is supported.
    # We check auth manually in the body to control close codes better.
):
    # 1. Accept / Handshake (Or reject)
    # Extract User ID from Query Param (Stub)
    user_id_str = websocket.query_params.get("x_user_id")
    if not user_id_str:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing Auth")
        return

    try:
        user_uuid = UUID(user_id_str)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid User ID")
        return

    # 2. Verify Membership
    async with async_session_factory() as session:
        # Check thread exists & match participation
        stmt = sql_select(Thread).where(Thread.id == thread_id)
        result = await session.execute(stmt)
        thread = result.scalar_one_or_none()
        
        if not thread:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Thread not found")
            return

        stmt = sql_select(Match).where(Match.id == thread.match_id)
        result = await session.execute(stmt)
        match = result.scalar_one_or_none()
        
        if not match:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Match not found")
            return
            
        if match.user_a_id != user_uuid and match.user_b_id != user_uuid:
             await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Not authorized")
             return

    # 3. Connection Limits (Redis)
    conn_key = f"ws_conns:{user_uuid}"
    # Atomic increment and check
    current_conns = await redis.incr(conn_key)
    if current_conns == 1:
        await redis.expire(conn_key, 3600)  # TTL sanitation
        
    if current_conns > 5:
        await redis.decr(conn_key)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Too many connections")
        return

    # 4. Accept Connection
    await websocket.accept()
    
    # 5. Subscribe Loop (PubSub)
    pubsub = PubSubService(redis)
    channel = f"thread:{thread_id}"
    
    try:
        # We need to multiplex reading from WS (ping/close) and reading from PubSub
        # Tasks:
        # 1. Receive from PubSub -> Send to WS
        # 2. Receive from WS -> Ignore/Ping -> Close on disconnect
        
        subscriber_iter = pubsub.subscribe(channel)
        
        async def listen_to_redis():
            async for raw_msg in subscriber_iter:
                # raw_msg is JSON string
                await websocket.send_text(raw_msg)
                
        async def listen_to_client():
            async for _ in websocket.iter_text():
                # We ignore client messages as per "Read-Only" rule
                # But iterating keeps the connection alive/detects close
                pass

        # Run both
        redis_task = asyncio.create_task(listen_to_redis())
        client_task = asyncio.create_task(listen_to_client())
        
        done, pending = await asyncio.wait(
            [redis_task, client_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cleanup
        for task in pending:
            task.cancel()
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        # print(f"WS Error: {e}")
        pass
    finally:
        # Decr usage
        await redis.decr(conn_key)
        await pubsub.disconnect()
