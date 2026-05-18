"""
Handler: Client Content
GET /clients/{client_id}/content/ - List content generated for client
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_client_content(
    client_id: str,
    limit: int = 20,
    offset: int = 0,
    content_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get content generated for this client

    Args:
        client_id: Client UUID
        limit: Results per page
        offset: Pagination offset
        content_type: Filter by type (all|post|video|email|story)

    Returns:
        Dict with content array and total count

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Build query
        query = supabase.client.table("content_lab_generated")\
            .select("*", count="exact")\
            .eq("client_id", client_id)\
            .order("created_at.desc")

        if content_type and content_type != "all":
            query = query.eq("type", content_type)

        query = query.range(offset, offset + limit - 1)
        content_resp = query.execute()

        content_data = content_resp.data or []
        content = [
            {
                "id": item.get("id"),
                "type": item.get("type"),
                "platform": item.get("platform"),
                "agent_code": item.get("agent_code"),
                "status": item.get("status"),
                "created_at": item.get("created_at")
            }
            for item in content_data
        ]

        return {"content": content, "total": content_resp.count or 0}

    except Exception as e:
        logger.error(f"Error getting client content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get client content: {str(e)}")
