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
    - total_agents: Active agents in database
    - active_agents: Agents with status='active'
    - total_clients: Active clients
    - total_scheduled_posts: Active scheduled posts
    - content_generated_today: Content created today
    - agent_executions_today: Agent executions today
    """
    return await handle_get_stats(request.app)
