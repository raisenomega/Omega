"""
Handler: Get Scan History
Retorna historial de scans con paginación
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_history(limit: int = 30, agent_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Get scan history with pagination

    Args:
        limit: Number of records to return
        agent_code: Optional filter by agent

    Returns:
        Dict with scan history

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Build query
        query = supabase.client.table("sentinel_scans")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(min(limit, 100))  # Max 100

        # Filter by agent if provided
        if agent_code:
            query = query.eq("agent_code", agent_code.upper())

        # Execute query
        resp = query.execute()
        scans = resp.data or []

        logger.info(f"Retrieved {len(scans)} scan records")

        return {
            "total": len(scans),
            "scans": scans,
            "filtered_by": agent_code if agent_code else "all"
        }

    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scan history: {str(e)}"
        )
