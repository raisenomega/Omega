"""
Handler: Save NOVA Data
UPSERT data into nova_data table
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Union, List
from fastapi import HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class SaveDataRequest(BaseModel):
    data_type: str
    content: Union[List, Dict]


async def handle_save_data(request: SaveDataRequest) -> Dict[str, Any]:
    """
    Save/update NOVA data using UPSERT pattern

    Args:
        request: SaveDataRequest with data_type and content

    Returns:
        Dict with success status, data_type, and updated_at

    Raises:
        HTTPException 400: Invalid request
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()
        user_id = "ibrain"

        # Validate data_type
        valid_types = ["chat_history", "context_docs", "reports"]
        if request.data_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_type. Must be one of: {valid_types}"
            )

        # Prepare upsert data
        now = datetime.utcnow().isoformat()
        upsert_data = {
            "user_id": user_id,
            "data_type": request.data_type,
            "content": request.content,
            "updated_at": now
        }

        # UPSERT: Insert or update on conflict
        resp = supabase.client.table("nova_data")\
            .upsert(upsert_data, on_conflict="user_id,data_type")\
            .execute()

        if not resp.data:
            raise Exception("Upsert returned no data")

        logger.info(f"Saved NOVA data: type={request.data_type}, size={len(str(request.content))}")

        return {
            "success": True,
            "data_type": request.data_type,
            "updated_at": now
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving NOVA data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save NOVA data: {str(e)}"
        )
