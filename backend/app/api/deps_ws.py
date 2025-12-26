from typing import Annotated
from fastapi import Depends
from redis.asyncio import Redis
from app.db.redis import get_redis_pool
from app.services.pubsub import PubSubService

async def get_pubsub_service(redis: Annotated[Redis, Depends(get_redis_pool)]) -> PubSubService:
    return PubSubService(redis)

PubSubDep = Annotated[PubSubService, Depends(get_pubsub_service)]
