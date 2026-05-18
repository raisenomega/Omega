"""
Handoff Handlers — Business logic for inter-agent delegation.
DDD: Application layer handlers.
"""
from .create_handoff import handle_create_handoff
from .confirm_complete import handle_confirm_handoff, handle_complete_handoff
from .get_handoffs import handle_get_pending, handle_get_handoff

__all__ = [
    "handle_create_handoff",
    "handle_confirm_handoff",
    "handle_complete_handoff",
    "handle_get_pending",
    "handle_get_handoff"
]
