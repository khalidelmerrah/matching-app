from fastapi import APIRouter
from app.api.endpoints import threads, ws  # <--- Import ws

api_router = APIRouter()

# Existing threads router
api_router.include_router(threads.router, prefix="/threads", tags=["threads"])

# NEW: Add WS router
# Resulting URL: /api/v1/ws/threads/{id}
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])