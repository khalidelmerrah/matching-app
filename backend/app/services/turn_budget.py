import redis.asyncio as redis

# Lua script for atomic check-and-decrement
# Keys: {turn_budget_key}
# Args: {cost}, {ttl}
# Returns:
#   -2: Key does not exist (Budget not initialized)
#   -1: Budget exhausted (current < cost)
#   >=0: New remaining budget
TURN_BUDGET_SCRIPT = """
local budget = redis.call('get', KEYS[1])
if not budget then
    return -2
end

budget = tonumber(budget)
local cost = tonumber(ARGV[1])

if budget < cost then
    return -1
end

local new_budget = redis.call('decrby', KEYS[1], cost)
-- Refresh TTL if needed (optional, but good for active threads)
-- redis.call('expire', KEYS[1], ARGV[2])
return new_budget
"""

class TurnBudgetService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.script_check_decr = self.redis.register_script(TURN_BUDGET_SCRIPT)

    def _get_key(self, user_id: str, match_id: str) -> str:
        return f"turn_budget:{user_id}:{match_id}"

    async def initialize_budget(self, user_id: str, match_id: str, amount: int, ttl: int = 86400) -> bool:
        """
        Initialize budget for a user in a match.
        Uses SET NX to avoid overwriting existing budget.
        """
        key = self._get_key(user_id, match_id)
        # SET key value NX EX ttl
        result = await self.redis.set(key, amount, nx=True, ex=ttl)
        return bool(result)

    async def check_and_consume(self, user_id: str, match_id: str, cost: int = 1) -> int:
        """
        Atomically check and consume turns.
        Returns:
            -2: Budget not initialized
            -1: Budget exhausted
            >=0: Remaining budget
        """
        key = self._get_key(user_id, match_id)
        # Using a default TTL for script arg if needed, currently script doesn't force expire update
        result = await self.script_check_decr(keys=[key], args=[cost, 86400])
        return int(result)
        
    async def get_remaining(self, user_id: str, match_id: str) -> int:
        """Check budget without consuming."""
        key = self._get_key(user_id, match_id)
        val = await self.redis.get(key)
        return int(val) if val is not None else -2
