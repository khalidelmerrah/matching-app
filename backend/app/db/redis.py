import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

async def get_redis_pool() -> redis.Redis:
    return redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
