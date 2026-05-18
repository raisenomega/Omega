"""
Handler: Get All Agents with Stats
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_agents() -> Dict[str, Any]:
    """
    Get all agents organized by department with stats

    Returns:
        Dict with agents list, by_department grouping, and stats

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get all active agents
        agents_resp = supabase.client.table("agents")\
            .select("*")\
            .eq("is_active", True)\
            .order("department, agent_id")\
            .execute()
        agents_data = agents_resp.data or []

        # Group by department
        by_department = {}
        for agent in agents_data:
            dept = agent.get("department", "unknown")
            if dept not in by_department:
                by_department[dept] = []
            by_department[dept].append({
                "id": agent.get("id"),
                "agent_id": agent.get("agent_id"),
                "name": agent.get("name"),
                "description": agent.get("description"),
                "status": agent.get("status"),
                "category": agent.get("category")
            })

        # Count by status
        active_count = sum(1 for a in agents_data if a.get("status") == "active")
        running_count = sum(1 for a in agents_data if a.get("status") == "running")
        inactive_count = sum(1 for a in agents_data if a.get("status") == "inactive")

        logger.info(f"Retrieved {len(agents_data)} agents across {len(by_department)} departments")

        return {
            "total": len(agents_data),
            "by_department": by_department,
            "stats": {
                "active": active_count,
                "running": running_count,
                "inactive": inactive_count
            },
            "departments": list(by_department.keys())
        }

    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")
