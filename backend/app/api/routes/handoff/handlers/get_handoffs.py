"""
Get Handoffs Handlers — Query operations for handoff tasks.
DDD: Application layer - read operations.
Strict <200L per file.
"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from app.services.handoff_service import HandoffService
from ..models import HandoffResponse, HandoffListResponse
import logging

logger = logging.getLogger(__name__)


async def handle_get_pending(agent_code: str) -> HandoffListResponse:
    """
    Retrieves all pending handoffs for an agent.

    Use this endpoint for agents to check their task queue.
    """
    try:
        supabase = get_supabase_service()
        handoff_service = HandoffService(supabase)

        handoffs = handoff_service.get_pending_handoffs(agent_code)

        handoff_responses = [
            HandoffResponse(
                task_id=h.task_id,
                from_agent=h.from_agent,
                to_agent=h.to_agent,
                task_type=h.task_type,
                payload=h.payload,
                priority=h.priority.value,
                status=h.status.value,
                created_at=h.created_at,
                deadline=h.deadline
            )
            for h in handoffs
        ]

        logger.info(f"Retrieved {len(handoffs)} pending handoffs for {agent_code}")

        return HandoffListResponse(
            handoffs=handoff_responses,
            count=len(handoff_responses)
        )

    except Exception as e:
        logger.error(f"Error fetching pending handoffs for {agent_code}: {e}")
        raise HTTPException(500, f"Error fetching handoffs: {str(e)}")


async def handle_get_handoff(task_id: str) -> HandoffResponse:
    """
    Retrieves a specific handoff by task_id.
    """
    try:
        supabase = get_supabase_service()
        handoff_service = HandoffService(supabase)

        handoff = handoff_service._get_handoff(task_id)

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
        logger.error(f"Handoff {task_id} not found: {e}")
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"Error fetching handoff {task_id}: {e}")
        raise HTTPException(500, f"Error fetching handoff: {str(e)}")
