import asyncio
import json
from typing import AsyncIterator, Optional

from redis.asyncio import Redis
from app.db.redis import get_redis_pool

class PubSubService:
    def __init__(self, redis: Redis):
        self.redis = redis
        self._pubsub = None

    async def publish(self, channel: str, message: dict | str) -> None:
        if isinstance(message, dict):
            message = json.dumps(message)
        await self.redis.publish(channel, message)

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(channel)
        
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    yield message["data"]
        finally:
            await self._pubsub.unsubscribe(channel)
            await self._pubsub.close()

    async def disconnect(self):
        if self._pubsub:
            await self._pubsub.close()
