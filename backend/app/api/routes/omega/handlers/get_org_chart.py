"""
Handler: OMEGA Company Org Chart
45 organizational agents by department with hierarchy
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_org_chart() -> Dict[str, Any]:
    """
    Get OMEGA Company organizational chart

    Returns:
        Dict with agents grouped by department showing hierarchy

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get all organizational agents
        agents_resp = supabase.client.table("omega_agents")\
            .select("*")\
            .order("department, role.desc, agent_code")\
            .execute()
        agents_data = agents_resp.data or []

        # Build hierarchy by department
        org_chart = {}
        for agent in agents_data:
            dept = agent.get("department", "unknown")
            if dept not in org_chart:
                org_chart[dept] = {"director": None, "sub_agents": []}

            agent_info = {
                "agent_code": agent.get("agent_code"),
                "name": agent.get("name"),
                "role": agent.get("role"),
                "reports_to": agent.get("reports_to"),
                "status": agent.get("status"),
                "description": agent.get("description"),
                "performance_score": agent.get("performance_score", 0),
                "tasks_completed_total": agent.get("tasks_completed_total", 0),
                "is_promotable": agent.get("is_promotable", False)
            }

            if agent.get("role") == "director":
                org_chart[dept]["director"] = agent_info
            else:
                org_chart[dept]["sub_agents"].append(agent_info)

        # Count stats
        directors = sum(1 for a in agents_data if a.get("role") == "director")
        sub_agents = sum(1 for a in agents_data if a.get("role") == "sub_agent")
        active = sum(1 for a in agents_data if a.get("status") == "active")

        logger.info(f"Org chart: {len(agents_data)} agents, {directors} directors, {len(org_chart)} departments")

        return {
            "total_agents": len(agents_data),
            "directors": directors,
            "sub_agents": sub_agents,
            "active_count": active,
            "departments": list(org_chart.keys()),
            "org_chart": org_chart
        }

    except Exception as e:
        logger.error(f"Error getting org chart: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get org chart: {str(e)}")
