"""
Handler: Get NOVA Data
Retrieve data from nova_data table filtered by type
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, Query
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_data(data_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get NOVA data filtered by type

    Args:
        data_type: Optional filter (chat_history | context_docs | reports)

    Returns:
        Dict with data_type, content, and updated_at
        If not found, returns empty content

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()
        user_id = "ibrain"

        # Build query
        query = supabase.client.table("nova_data")\
            .select("data_type, content, updated_at")\
            .eq("user_id", user_id)

        # Filter by type if provided
        if data_type:
            query = query.eq("data_type", data_type)

        # Execute query
        resp = query.execute()
        data = resp.data or []

        if not data:
            # Return empty result if no data found
            return {
                "data_type": data_type or "all",
                "content": [],
                "updated_at": None
            }

        # If single type requested, return first result
        if data_type and len(data) > 0:
            result = data[0]
            logger.info(f"Retrieved NOVA data: type={data_type}")
            return result

        # If no type filter, return all records
        logger.info(f"Retrieved {len(data)} NOVA data records")
        return {"records": data, "total": len(data)}

    except Exception as e:
        logger.error(f"Error getting NOVA data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get NOVA data: {str(e)}"
        )
