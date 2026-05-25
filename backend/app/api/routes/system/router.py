"""
System Router - Dynamic system statistics
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Request
from .handlers.get_stats import handle_get_stats

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/stats")
async def get_system_stats(request: Request):
    """
    Get dynamic system statistics

    Returns real-time counts of:
    - total_endpoints: FastAPI routes count
    - total_agents / active_agents: agents with is_active=True
    - total_clients: clients (all · borrado es hard-delete)
    - total_scheduled_posts: scheduled posts activos (status='pending')
    - content_generated_today: content created today

    Cada count está aislado (degradación parcial · una query rota → 0, no 500).
    """
    return await handle_get_stats(request.app)
