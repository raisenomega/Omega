"""
OMEGA Company Handlers
"""
from .get_dashboard import handle_get_omega_dashboard
from .get_resellers import handle_get_resellers
from .get_clients import handle_get_clients
from .get_revenue import handle_get_revenue
from .get_activity import handle_get_activity
from .get_agents import handle_get_agents
from .get_org_chart import handle_get_org_chart
from .generate_dept_report import handle_generate_dept_report
from .handle_trigger_worker import handle_trigger_worker

__all__ = [
    "handle_get_omega_dashboard",
    "handle_get_resellers",
    "handle_get_clients",
    "handle_get_revenue",
    "handle_get_activity",
    "handle_get_agents",
    "handle_get_org_chart",
    "handle_generate_dept_report",
    "handle_trigger_worker"
]
