import asyncio
import json
import pytest
from httpx import AsyncClient
from redis.asyncio import Redis
from starlette.websockets import WebSocketDisconnect
from uuid import uuid4

@pytest.mark.asyncio
async def test_ws_auth_fail_no_token(client: AsyncClient, test_ctx):
    # Connect without token stub
    thread = test_ctx["thread"]
    
    with pytest.raises(WebSocketDisconnect) as exc:
        async with client.websocket_connect(f"/api/v1/ws/threads/{thread.id}") as websocket:
            pass
    assert exc.value.code == 1008  # Policy Violation

@pytest.mark.asyncio
async def test_ws_membership_fail_wrong_thread(client: AsyncClient, test_ctx):
    # User B tries to connect to a random non-existent or unrelated thread
    random_thread_id = uuid4()
    user_id = test_ctx["user_b"].id
    
    with pytest.raises(WebSocketDisconnect) as exc:
        async with client.websocket_connect(
            f"/api/v1/ws/threads/{random_thread_id}?x_user_id={user_id}"
        ) as websocket:
            pass
    assert exc.value.code == 1008

@pytest.mark.asyncio
async def test_ws_broadcast_flow(client: AsyncClient, redis_client: Redis, test_ctx):
    # Setup
    user_owner = test_ctx["user_a"]
    user_sender = test_ctx["user_b"]
    thread = test_ctx["thread"]
    match = test_ctx["match"]
    
    # Needs budget
    from app.services.turn_budget import TurnBudgetService
    budget = TurnBudgetService(redis_client)
    await budget.initialize_budget(str(user_sender.id), str(match.id), 5)

    # 1. User A connects to WS
    ws_url = f"/api/v1/ws/threads/{thread.id}?x_user_id={user_owner.id}"
    
    async with client.websocket_connect(ws_url) as websocket:
        # 2. User B sends message via HTTP
        http_url = f"/api/v1/threads/{thread.id}/messages"
        headers = {
            "X-User-Id": str(user_sender.id),
            "Idempotency-Key": f"ws_test_{uuid4()}"
        }
        resp = await client.post(http_url, json={"content": "Hello WS"}, headers=headers)
        assert resp.status_code == 200
        msg_id = resp.json()["id"]

        # 3. User A receives event
        payload = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
        event = json.loads(payload)
        
        assert event["type"] == "message.created"
        assert event["thread_id"] == str(thread.id)
        assert event["message_id"] == msg_id
        # assert event["sender_id"] == str(user_sender.id)

@pytest.mark.asyncio
async def test_ws_concurrency_broadcast(client: AsyncClient, redis_client: Redis, test_ctx):
    # Two clients connected to same thread receive the message
    user_a = test_ctx["user_a"]
    user_b = test_ctx["user_b"]
    thread = test_ctx["thread"]
    
    # Budget for sender (A)
    # Re-init budget just in case shared scope issues
    from app.services.turn_budget import TurnBudgetService
    budget = TurnBudgetService(redis_client)
    await budget.initialize_budget(str(user_a.id), str(test_ctx["match"].id), 5)

    ws_url_a = f"/api/v1/ws/threads/{thread.id}?x_user_id={user_a.id}"
    ws_url_b = f"/api/v1/ws/threads/{thread.id}?x_user_id={user_b.id}"

    async with client.websocket_connect(ws_url_a) as ws_a, \
               client.websocket_connect(ws_url_b) as ws_b:
                   
        # A posts, both should receive? Actually usually sender also receives broadcast in simple pubsub
        # The logic doesn't exclude sender. 
        http_url = f"/api/v1/threads/{thread.id}/messages"
        headers = {
            "X-User-Id": str(user_a.id),
            "Idempotency-Key": f"ws_conc_{uuid4()}"
        }
        resp = await client.post(http_url, json={"content": "Broadcast to all"}, headers=headers)
        assert resp.status_code == 200
        
        # Verify A received
        msg_a = await asyncio.wait_for(ws_a.receive_text(), timeout=2.0)
        assert "message.created" in msg_a
        
        # Verify B received
        msg_b = await asyncio.wait_for(ws_b.receive_text(), timeout=2.0)
        assert "message.created" in msg_b

