"""
Handler: Get All Clients with Pagination
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_clients(
    reseller_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get all clients with pagination and filtering

    Args:
        reseller_id: Filter by reseller UUID
        status: Filter by status
        limit: Results per page
        offset: Pagination offset

    Returns:
        Dict with clients list and total count
    """
    try:
        supabase = get_supabase_service()

        # Build query
        query = supabase.client.table("clients")\
            .select("*")\
            .neq("status", "deleted")

        if reseller_id:
            query = query.eq("reseller_id", reseller_id)
        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True)\
            .range(offset, offset + limit - 1)

        resp = query.execute()
        clients_data = resp.data or []

        # Get total count
        count_query = supabase.client.table("clients")\
            .select("id", count="exact")\
            .neq("status", "deleted")

        if reseller_id:
            count_query = count_query.eq("reseller_id", reseller_id)
        if status:
            count_query = count_query.eq("status", status)

        count_resp = count_query.execute()
        total = count_resp.count if count_resp.count else 0

        logger.info(f"Retrieved {len(clients_data)} clients (total: {total})")

        return {
            "clients": clients_data,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get clients: {str(e)}")
