"""
Handler: Get Resellers List with Metrics
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_resellers(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get resellers list with client counts and metrics

    Args:
        status: Filter by status (active, trial, inactive)
        limit: Results per page
        offset: Pagination offset

    Returns:
        Dict with resellers list and total count
    """
    try:
        supabase = get_supabase_service()

        # Build query
        query = supabase.client.table("resellers")\
            .select("*")

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True)\
            .range(offset, offset + limit - 1)

        resp = query.execute()
        resellers_data = resp.data or []

        # Get client counts for each reseller
        clients_resp = supabase.client.table("clients")\
            .select("reseller_id")\
            .neq("status", "deleted")\
            .execute()
        clients_data = clients_resp.data or []

        # Count clients per reseller
        client_counts = {}
        for c in clients_data:
            rid = c.get("reseller_id")
            if rid:
                client_counts[rid] = client_counts.get(rid, 0) + 1

        # Enrich resellers with client counts
        for r in resellers_data:
            r["clients_count"] = client_counts.get(r["id"], 0)

        # Get total count
        count_resp = supabase.client.table("resellers")\
            .select("id", count="exact")\
            .execute()
        total = count_resp.count if count_resp.count else 0

        logger.info(f"Retrieved {len(resellers_data)} resellers (total: {total})")

        return {
            "resellers": resellers_data,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting resellers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get resellers: {str(e)}")
