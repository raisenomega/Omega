"""
Create Handoff Handler — Creates new inter-agent task delegations.
DDD: Application layer - create operations.
Strict <200L per file.
"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from app.services.handoff_service import HandoffService
from ..models import HandoffCreateRequest, HandoffResponse
import logging

logger = logging.getLogger(__name__)


async def handle_create_handoff(request: HandoffCreateRequest) -> HandoffResponse:
    """
    Creates structured handoff between agents.

    Protocol:
    1. NOVA → ATLAS: Strategic content brief
    2. ATLAS → RAFA: Content generation task
    3. SENTINEL → NOVA: Security alerts
    4. REX → ANCHOR: Churn intervention
    """
    try:
        supabase = get_supabase_service()
        handoff_service = HandoffService(supabase)

        handoff = handoff_service.create_handoff(
            from_agent=request.from_agent,
            to_agent=request.to_agent,
            task_type=request.task_type,
            payload=request.payload,
            priority=request.priority,
            deadline=request.deadline
        )

        logger.info(
            f"Handoff created: {handoff.task_id} | "
            f"{request.from_agent} → {request.to_agent} | "
            f"type={request.task_type}"
        )

        return HandoffResponse(
            task_id=handoff.task_id,
            from_agent=handoff.from_agent,
            to_agent=handoff.to_agent,
            task_type=handoff.task_type,
            payload=handoff.payload,
            priority=handoff.priority.value,
            status=handoff.status.value,
            created_at=handoff.created_at,
            deadline=handoff.deadline
        )

    except ValueError as e:
        logger.error(f"Validation error creating handoff: {e}")
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error creating handoff: {e}")
        raise HTTPException(500, f"Error creating handoff: {str(e)}")
