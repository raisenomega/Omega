"""Client Detail Handlers Package"""
from .get_client_detail import handle_get_client_detail
from .get_client_agents import handle_get_client_agents
from .assign_client_agents import handle_assign_client_agents
from .get_client_content import handle_get_client_content
from .get_client_billing import handle_get_client_billing
from .get_client_activity import handle_get_client_activity

__all__ = [
    "handle_get_client_detail",
    "handle_get_client_agents",
    "handle_assign_client_agents",
    "handle_get_client_content",
    "handle_get_client_billing",
    "handle_get_client_activity"
]
