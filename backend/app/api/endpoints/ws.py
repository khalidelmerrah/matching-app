from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.deps_ws import get_current_user_ws, PubSubDep
from app.services.pubsub import PubSubService
from app.models import Message, Thread, Match, User
import asyncio
import json

router = APIRouter()

@router.websocket("/threads/{thread_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    thread_id: str,
    pubsub_service: PubSubDep,
    user_id: str | None = Depends(get_current_user_ws),
):
    if user_id is None:
        return  # Connection rejected in dependency check

    await websocket.accept()
    channel = f"thread:{thread_id}"

    try:
        # Subscribe returns an async iterator that yields messages
        async for message in pubsub_service.subscribe(channel):
            # message is already "data" string from redis
            await websocket.send_text(message)
    except WebSocketDisconnect:
        # The iterator's finally block handles unsubscribe/close
        pass
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.close()
        except:
            pass