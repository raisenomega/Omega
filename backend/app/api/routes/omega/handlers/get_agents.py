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

        # Get all active agents (DEBT-080: cols reales de la tabla agents)
        agents_resp = supabase.client.table("agents")\
            .select("*")\
            .eq("is_active", True)\
            .order("category, code")\
            .execute()
        agents_data = agents_resp.data or []

        # Group by category (la tabla no tiene `department`)
        by_category = {}
        for agent in agents_data:
            cat = agent.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            is_active = agent.get("is_active", True)
            by_category[cat].append({
                "id": agent.get("id"),
                "code": agent.get("code"),
                "name": agent.get("name"),
                "description": agent.get("description"),
                "status": "active" if is_active else "inactive",
                "category": agent.get("category")
            })

        # Count by status derived from is_active (no existe col `status`)
        active_count = sum(1 for a in agents_data if a.get("is_active", True))
        inactive_count = sum(1 for a in agents_data if not a.get("is_active", True))

        logger.info(f"Retrieved {len(agents_data)} agents across {len(by_category)} categories")

        return {
            "total": len(agents_data),
            "by_category": by_category,
            "stats": {
                "active": active_count,
                "inactive": inactive_count
            },
            "categories": list(by_category.keys())
        }

    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")
