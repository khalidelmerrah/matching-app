from app.api.endpoints import threads, ws

api_router = APIRouter()
api_router.include_router(threads.router, prefix="/threads", tags=["threads"])
api_router.include_router(ws.router, tags=["websockets"])
