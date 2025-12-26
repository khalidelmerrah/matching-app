from enum import Enum

class MatchState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    UNMATCHED = "unmatched"

class ThreadState(str, Enum):
    INITIALIZING = "initializing"
    BLIND_VOLLEY = "blind_volley"  # First interaction
    ESTABLISHED = "established"    # Regular conversation
    SUSPENDED = "suspended"        # Paused or blocked
    CLOSED = "closed"

class RevealLevel(int, Enum):
    BLURRED = 0
    PARTIAL = 1
    FULL = 2
