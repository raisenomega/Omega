"""
Handler: Client Activity
GET /clients/{client_id}/activity/ - Activity feed for client
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_client_activity(
    client_id: str,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get recent activity for this client

    Args:
        client_id: Client UUID
        limit: Results per page
        offset: Pagination offset

    Returns:
        Dict with activities array and total count

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get activities from content_lab_generated as proxy
        content_resp = supabase.client.table("content_lab_generated")\
            .select("*", count="exact")\
            .eq("client_id", client_id)\
            .order("created_at.desc")\
            .range(offset, offset + limit - 1)\
            .execute()

        content_data = content_resp.data or []
        activities = [
            {
                "type": "content_generated",
                "description": f"{item.get('agent_code', 'Agent')} generó {item.get('type', 'content')} para {item.get('platform', 'platform')}",
                "agent_code": item.get("agent_code"),
                "timestamp": item.get("created_at")
            }
            for item in content_data
        ]

        return {"activities": activities, "total": content_resp.count or 0}

    except Exception as e:
        logger.error(f"Error getting client activity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get client activity: {str(e)}")
