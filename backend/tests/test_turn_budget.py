import asyncio
import uuid
import pytest
from httpx import AsyncClient
from redis.asyncio import Redis

from app.services.turn_budget import TurnBudgetService

@pytest.mark.asyncio
async def test_turn_budget_parallel_enforcement(client: AsyncClient, redis_client: Redis, test_ctx):
    # Setup
    user = test_ctx["user_a"]
    thread = test_ctx["thread"]
    match = test_ctx["match"]
    
    # Initialize budget to 5
    service = TurnBudgetService(redis_client)
    await service.initialize_budget(str(user.id), str(match.id), 5)
    
    # Send 20 concurrent messages
    tasks = []
    url = f"/api/v1/threads/{thread.id}/messages"
    headers = {"X-User-Id": str(user.id)} # Auth stub
    
    for i in range(20):
        # Unique idempotency key for each request
        idem_key = f"parallel_{uuid.uuid4()}"
        payload = {"content": f"msg {i}"}
        tasks.append(
            client.post(url, json=payload, headers={**headers, "Idempotency-Key": idem_key})
        )
        
    responses = await asyncio.gather(*tasks)
    
    # Verify results
    success_count = sum(1 for r in responses if r.status_code == 200)
    exhausted_count = sum(1 for r in responses if r.status_code == 400 and r.headers.get("X-Error-Code") == "TURN_BUDGET_EXHAUSTED")
    
    assert success_count == 5, f"Expected exactly 5 successes, got {success_count}"
    assert exhausted_count >= 15, "Expected failures due to budget exhaustion"
    
    # Verify remaining budget is 0 (not negative)
    remaining = await service.get_remaining(str(user.id), str(match.id))
    assert remaining == 0

@pytest.mark.asyncio
async def test_idempotency_retry_does_not_consume_turn(client: AsyncClient, redis_client: Redis, test_ctx):
    # Setup
    user = test_ctx["user_b"]
    thread = test_ctx["thread"]
    match = test_ctx["match"]
    
    # Initialize budget to 5
    service = TurnBudgetService(redis_client)
    await service.initialize_budget(str(user.id), str(match.id), 5)
    
    url = f"/api/v1/threads/{thread.id}/messages"
    headers = {"X-User-Id": str(user.id), "Idempotency-Key": "retry_test_key"} # Same key
    payload = {"content": "idempotent msg"}
    
    # First Request
    resp1 = await client.post(url, json=payload, headers=headers)
    assert resp1.status_code == 200
    
    # Verify budget consumed (5 -> 4)
    remaining = await service.get_remaining(str(user.id), str(match.id))
    assert remaining == 4
    
    # Second Request (Retry)
    resp2 = await client.post(url, json=payload, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == resp1.json()["id"] # Same message ID
    
    # Verify budget NOT consumed again (Still 4)
    remaining_after = await service.get_remaining(str(user.id), str(match.id))
    assert remaining_after == 4
