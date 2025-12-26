import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.db.redis import get_redis_pool
from app.main import app
from app.db.models import User, Match, Thread, ThreadState

# Set asyncio mode
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

@pytest.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    client = await get_redis_pool()
    yield client
    await client.close()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture
async def setup_data(db_session: AsyncSession, redis_client: Redis):
    # Clear DB (truncate) - dangerous in prod, safe in test container
    # But for now we just create new data
    pass
    
# Helper to create test user/match/thread
@pytest.fixture
async def test_ctx(db_session: AsyncSession):
    user_a = User(phone="111", role="user")
    user_b = User(phone="222", role="user")
    db_session.add(user_a)
    db_session.add(user_b)
    await db_session.flush()
    
    match = Match(user_a_id=user_a.id, user_b_id=user_b.id, score=0.9)
    db_session.add(match)
    await db_session.flush()
    
    thread = Thread(match_id=match.id, current_state=ThreadState.BLIND_VOLLEY)
    db_session.add(thread)
    await db_session.commit()
    
    return {
        "user_a": user_a,
        "user_b": user_b,
        "match": match,
        "thread": thread
    }
