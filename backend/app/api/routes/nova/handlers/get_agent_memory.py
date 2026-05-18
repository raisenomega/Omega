"""
Handler: Get Agent Memory
Retrieve last 10 memory entries for an agent
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_agent_memory(agent_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Get agent memory entries

    Args:
        agent_code: Optional filter by agent code (e.g., 'NOVA', 'ATLAS')

    Returns:
        Dict with memories list (last 10 entries, newest first)

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Build query
        query = supabase.client.table("omega_agent_memory")\
            .select("*")\
            .order("updated_at", desc=True)\
            .limit(10)

        # Filter by agent_code if provided
        if agent_code:
            query = query.eq("agent_code", agent_code.upper())

        # Execute query
        resp = query.execute()
        memories = resp.data or []

        logger.info(f"Retrieved {len(memories)} memory entries for agent={agent_code or 'all'}")

        return {
            "agent_code": agent_code,
            "total": len(memories),
            "memories": memories
        }

    except Exception as e:
        logger.error(f"Error getting agent memory: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent memory: {str(e)}"
        )
