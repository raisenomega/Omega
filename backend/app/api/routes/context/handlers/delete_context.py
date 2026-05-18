"""Handler: Delete context document"""
import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_delete_context(context_id: str) -> Dict[str, Any]:
    """Delete context document (hard delete)."""
    try:
        supabase = get_supabase_service()
        resp = supabase.client.table("context_library")\
            .delete()\
            .eq("id", context_id)\
            .execute()
        if not resp.data:
            raise HTTPException(404, "Context not found")
        logger.info(f"Deleted context: {context_id}")
        return {"deleted": True, "id": context_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete context: {e}")
        raise HTTPException(500, f"Failed to delete context: {str(e)}")
