"""
Save NOVA Memory Handler — NOVA-specific memory endpoint.
Extends existing /agent-memory/ but always uses agent_code="NOVA".
Filosofía: No velocity, only precision 🐢💎
DDD: Application layer. Strict <200L.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.infrastructure.supabase_service import get_supabase_service
import logging

logger = logging.getLogger(__name__)


class SaveNovaMemoryRequest(BaseModel):
    """NOVA-specific memory save request"""
    memory_type: str = Field(..., description="decision|operational_rule|client_context|performance")
    content: str = Field(..., min_length=1, description="Memory content")
    related_agents: List[str] = Field(default=[], description="Related agent codes")
    client_id: Optional[str] = Field(None, description="Client UUID if relevant")
    priority: str = Field(default="medium", description="high|medium|low")
    expires_at: Optional[str] = Field(None, description="ISO8601 expiration (null=permanent)")


async def handle_save_nova_memory(request: SaveNovaMemoryRequest) -> Dict[str, Any]:
    """
    Save NOVA memory entry to omega_agent_memory table.
    Always sets agent_code="NOVA".

    Returns:
        {"id": "uuid", "agent_code": "NOVA", "saved": true}
    """
    try:
        supabase = get_supabase_service()

        # Build memory entry (always NOVA)
        memory_entry = {
            "agent_code": "NOVA",
            "memory_type": request.memory_type,
            "content": request.content,
            "related_agents": request.related_agents,
            "priority": request.priority.lower(),
            "expires_at": request.expires_at,
            "created_at": datetime.utcnow().isoformat()
        }

        # Only include client_id if provided (UUID field requires valid UUID or null)
        if request.client_id and request.client_id.strip():
            memory_entry["client_id"] = request.client_id

        # Save to omega_agent_memory
        resp = supabase.client.table("agent_working_memory")\
            .insert(memory_entry)\
            .execute()

        if not resp.data:
            raise ValueError("Failed to save NOVA memory")

        memory_id = resp.data[0]["id"]

        logger.info(f"NOVA memory saved: {memory_id} (type={request.memory_type}, priority={request.priority})")

        return {
            "id": memory_id,
            "agent_code": "NOVA",
            "saved": True
        }

    except Exception as e:
        logger.error(f"Error saving NOVA memory: {e}")
        raise ValueError(f"Failed to save NOVA memory: {str(e)}")
