"""
NOVA Execute Action Handler — Enable NOVA to take actions via API.
Supports: create_handoff, save_memory, get_briefing.
Future: generate_content, delegate_to_atlas (Phase 2).
Filosofía: No velocity, only precision 🐢💎
DDD: Application layer. Strict <200L.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException
from datetime import datetime
from app.infrastructure.supabase_service import get_supabase_service
from app.services.handoff_service import HandoffService
from .get_briefing import handle_get_briefing
from .save_nova_memory import handle_save_nova_memory, SaveNovaMemoryRequest
import logging

logger = logging.getLogger(__name__)


class ExecuteActionRequest(BaseModel):
    """NOVA action execution request"""
    action: str = Field(..., description="create_handoff|save_memory|get_briefing")
    target_agent: Optional[str] = Field(None, description="Target agent code (for handoffs)")
    payload: Dict[str, Any] = Field(default={}, description="Action-specific payload")


async def handle_execute_action(request: ExecuteActionRequest) -> Dict[str, Any]:
    """
    Execute NOVA actions.

    Supported actions:
    - create_handoff: Delegate task to another agent
    - save_memory: Save to NOVA memory
    - get_briefing: Refresh system snapshot

    Returns:
        Action-specific result + metadata

    Raises:
        HTTPException 422: Unimplemented action
        HTTPException 500: Execution error
    """
    try:
        supabase = get_supabase_service()

        # ACTION: create_handoff
        if request.action == "create_handoff":
            if not request.target_agent:
                raise ValueError("target_agent required for create_handoff")

            handoff_service = HandoffService(supabase)

            # Create handoff
            handoff = handoff_service.create_handoff(
                from_agent="NOVA",
                to_agent=request.target_agent,
                task_type=request.payload.get("task_type", "general"),
                payload=request.payload.get("data", {}),
                priority=(request.payload.get("priority") or "NORMAL").upper(),
                deadline=request.payload.get("deadline")
            )

            # Auto-save to NOVA memory
            memory_saved = False
            try:
                memory_entry = {
                    "agent_code": "NOVA",
                    "memory_type": "operational_rule",
                    "content": f"Delegated {request.payload.get('task_type')} to {request.target_agent}",
                    "related_agents": [request.target_agent],
                    "priority": (request.payload.get("priority") or "NORMAL").lower(),
                    "created_at": datetime.utcnow().isoformat()
                }
                supabase.client.table("agent_working_memory").insert(memory_entry).execute()
                memory_saved = True
            except Exception as e:
                logger.warning(f"Failed to save handoff memory: {e}")

            logger.info(f"NOVA executed create_handoff → {request.target_agent} (task_id={handoff.task_id})")

            return {
                "action": "create_handoff",
                "handoff_id": handoff.task_id,
                "status": handoff.status.value,
                "target_agent": request.target_agent,
                "memory_saved": memory_saved
            }

        # ACTION: save_memory
        elif request.action == "save_memory":
            # Validate client_id if provided
            client_id = request.payload.get("client_id")
            if client_id and not client_id.strip():
                client_id = None  # Convert empty string to None

            memory_request = SaveNovaMemoryRequest(
                memory_type=request.payload.get("memory_type", "operational_rule"),
                content=request.payload.get("content", ""),
                related_agents=request.payload.get("related_agents", []),
                client_id=client_id,
                priority=request.payload.get("priority", "medium"),
                expires_at=request.payload.get("expires_at")
            )

            result = await handle_save_nova_memory(memory_request)

            logger.info(f"NOVA executed save_memory (id={result['id']})")

            return {
                "action": "save_memory",
                "memory_id": result["id"],
                "saved": result["saved"]
            }

        # ACTION: get_briefing
        elif request.action == "get_briefing":
            briefing = await handle_get_briefing()

            logger.info("NOVA executed get_briefing (programmatic refresh)")

            return {
                "action": "get_briefing",
                "briefing": briefing
            }

        # UNIMPLEMENTED ACTIONS
        else:
            logger.warning(f"NOVA attempted unimplemented action: {request.action}")
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "action_not_implemented",
                    "action": request.action,
                    "supported_actions": ["create_handoff", "save_memory", "get_briefing"]
                }
            )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in execute_action: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing NOVA action '{request.action}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute action: {str(e)}")
