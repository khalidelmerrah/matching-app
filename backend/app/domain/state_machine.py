from app.domain.enums import ThreadState

def can_transition_thread(current: ThreadState, target: ThreadState) -> bool:
    """
    Pure function defining allowed thread state transitions.
    """
    if current == target:
        return True

    transitions = {
        ThreadState.INITIALIZING: {ThreadState.BLIND_VOLLEY},
        ThreadState.BLIND_VOLLEY: {ThreadState.ESTABLISHED, ThreadState.CLOSED},
        ThreadState.ESTABLISHED: {ThreadState.SUSPENDED, ThreadState.CLOSED},
        ThreadState.SUSPENDED: {ThreadState.ESTABLISHED, ThreadState.CLOSED},
        ThreadState.CLOSED: set(), # Termina state
    }

    return target in transitions.get(current, set())
