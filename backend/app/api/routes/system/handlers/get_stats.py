"""
Handler: Get System Stats
Dynamic system statistics - no hardcoding
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException, FastAPI
import logging
from datetime import date

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def count_routes(app: FastAPI) -> int:
    """Count total registered routes in FastAPI app"""
    return len([r for r in app.routes if hasattr(r, 'methods')])


async def handle_get_stats(app: FastAPI) -> Dict[str, Any]:
    """
    Get dynamic system statistics

    Returns:
        Dict with:
        - total_endpoints: Count of registered FastAPI routes
        - total_agents: Count of active agents in database
        - active_agents: Count of agents with status='active'
        - total_clients: Count of active clients
        - total_scheduled_posts: Count of active scheduled posts
        - content_generated_today: Count of content generated today
        - agent_executions_today: Count of agent executions today

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()
        today = date.today().isoformat()

        # 1. Count total endpoints (FastAPI routes)
        total_endpoints = count_routes(app)

        # 2. Count total agents (is_active=true)
        agents_resp = supabase.client.table("agents")\
            .select("id", count="exact")\
            .eq("is_active", True)\
            .execute()
        total_agents = agents_resp.count if agents_resp.count else 0

        # 3. Count active agents (status='active')
        active_agents_resp = supabase.client.table("agents")\
            .select("id", count="exact")\
            .eq("is_active", True)\
            .eq("status", "active")\
            .execute()
        active_agents = active_agents_resp.count if active_agents_resp.count else 0

        # 4. Count total clients (exclude deleted)
        clients_resp = supabase.client.table("clients")\
            .select("id", count="exact")\
            .neq("status", "deleted")\
            .execute()
        total_clients = clients_resp.count if clients_resp.count else 0

        # 5. Count scheduled posts (is_active=true)
        posts_resp = supabase.client.table("scheduled_posts")\
            .select("id", count="exact")\
            .eq("is_active", True)\
            .execute()
        total_scheduled_posts = posts_resp.count if posts_resp.count else 0

        # 6. Count content generated today
        content_today_resp = supabase.client.table("content_lab_generated")\
            .select("id", count="exact")\
            .gte("created_at", f"{today}T00:00:00")\
            .lte("created_at", f"{today}T23:59:59")\
            .execute()
        content_generated_today = content_today_resp.count if content_today_resp.count else 0

        # 7. Count agent executions today
        executions_today_resp = supabase.client.table("agent_executions")\
            .select("id", count="exact")\
            .gte("started_at", f"{today}T00:00:00")\
            .lte("started_at", f"{today}T23:59:59")\
            .execute()
        agent_executions_today = executions_today_resp.count if executions_today_resp.count else 0

        logger.info(f"System stats: {total_endpoints} endpoints, {total_agents} agents, {total_clients} clients")

        return {
            "total_endpoints": total_endpoints,
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_clients": total_clients,
            "total_scheduled_posts": total_scheduled_posts,
            "content_generated_today": content_generated_today,
            "agent_executions_today": agent_executions_today
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
