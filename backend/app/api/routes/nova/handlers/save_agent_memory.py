"""
Handler: Save Agent Memory
Insert new memory entry for an agent
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel
import logging
from datetime import datetime

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class SaveAgentMemoryRequest(BaseModel):
    agent_code: str
    memory_type: str
    content: Dict[str, Any]


async def handle_save_agent_memory(request: SaveAgentMemoryRequest) -> Dict[str, Any]:
    """
    Save new agent memory entry

    Args:
        request: SaveAgentMemoryRequest with agent_code, memory_type, content

    Returns:
        Dict with success status and inserted record id

    Raises:
        HTTPException 400: Invalid request
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Validate agent_code format (should be uppercase)
        agent_code = request.agent_code.upper()

        # Prepare insert data
        now = datetime.utcnow().isoformat()
        insert_data = {
            "agent_code": agent_code,
            "memory_type": request.memory_type,
            "content": request.content,
            "updated_at": now
        }

        # Insert new memory
        resp = supabase.client.table("omega_agent_memory")\
            .insert(insert_data)\
            .execute()

        if not resp.data or len(resp.data) == 0:
            raise Exception("Insert returned no data")

        record = resp.data[0]
        logger.info(f"Saved agent memory: agent={agent_code}, type={request.memory_type}")

        return {
            "success": True,
            "id": record.get("id"),
            "agent_code": agent_code,
            "updated_at": now
        }

    except Exception as e:
        logger.error(f"Error saving agent memory: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save agent memory: {str(e)}"
        )
