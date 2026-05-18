"""Handler: Get context for agent"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.services.context_service import ContextService

logger = logging.getLogger(__name__)

async def handle_get_context_for_agent(
    agent_code: str, client_id: Optional[str] = None, department: Optional[str] = None
) -> Dict[str, Any]:
    """Get all relevant context for an agent (global + client + department)."""
    try:
        service = ContextService()
        result = await service.get_context_for_agent(agent_code, client_id, department)
        logger.info(f"Retrieved context for agent {agent_code}: {len(result['sources'])} docs")
        return result
    except Exception as e:
        logger.error(f"Failed to get context for agent: {e}")
        raise HTTPException(500, f"Failed to get context for agent: {str(e)}")
