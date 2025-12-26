import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.main import app
from app.core.config import settings
from app.db.session import get_session
from app.db.redis import get_redis_pool
from app.models import User, Match, Thread, ThreadState, MatchStatus
from app.models.user import UserRole

# Use NullPool for tests to avoid AsyncPG concurrency issues
# This forces a fresh connection for every operation, ensuring isolation.
test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
)

TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    """
    Reset the database for every test function.
    This ensures no data leaks between tests (e.g. duplicate phone numbers).
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Optional: Drop again after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # Override the dependency to use the test session
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    
    # Use ASGITransport for direct app testing (faster/stable than standard transport)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest.fixture
async def redis_client():
    pool = await get_redis_pool()
    yield pool
    await pool.close()

@pytest.fixture
async def test_ctx(db_session: AsyncSession):
    # Create Users
    user_a = User(phone="+10000000000", role=UserRole.USER)
    user_b = User(phone="+10000000001", role=UserRole.USER)
    
    db_session.add(user_a)
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(user_a)
    await db_session.refresh(user_b)
    
    # Create Match
    match = Match(
        user_a_id=user_a.id,
        user_b_id=user_b.id,
        score=0.9,
        status=MatchStatus.active
    )
    db_session.add(match)
    await db_session.commit()
    await db_session.refresh(match)
    
    # Create Thread
    thread = Thread(
        match_id=match.id,
        current_state=ThreadState.BLIND_VOLLEY
    )
    db_session.add(thread)
    await db_session.commit()
    await db_session.refresh(thread)
    
    return {
        "user_a": user_a,
        "user_b": user_b,
        "match": match,
        "thread": thread
    }