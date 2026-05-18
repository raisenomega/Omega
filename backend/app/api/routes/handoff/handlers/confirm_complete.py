"""
Confirm/Complete Handlers — State transition operations for handoffs.
DDD: Application layer - state management.
Strict <200L per file.
"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from app.services.handoff_service import HandoffService
from ..models import (
    HandoffConfirmRequest,
    HandoffCompleteRequest,
    HandoffConfirmationResponse,
    HandoffCompletionResponse
)
import logging

logger = logging.getLogger(__name__)


async def handle_confirm_handoff(
    task_id: str,
    request: HandoffConfirmRequest
) -> HandoffConfirmationResponse:
    """
    Agent confirms receipt of handoff.

    Transitions: PENDING → IN_PROGRESS
    """
    try:
        supabase = get_supabase_service()
        handoff_service = HandoffService(supabase)

        confirmation = handoff_service.confirm_receipt(
            task_id=task_id,
            agent_code=request.agent_code
        )

        logger.info(f"Handoff {task_id} confirmed by {request.agent_code}")

        return HandoffConfirmationResponse(
            task_id=confirmation.task_id,
            confirmed_by=confirmation.confirmed_by,
            confirmed_at=confirmation.confirmed_at,
            status=confirmation.status.value
        )

    except ValueError as e:
        logger.error(f"Validation error confirming {task_id}: {e}")
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error confirming handoff {task_id}: {e}")
        raise HTTPException(500, f"Error confirming handoff: {str(e)}")


async def handle_complete_handoff(
    task_id: str,
    request: HandoffCompleteRequest
) -> HandoffCompletionResponse:
    """
    Agent marks handoff as complete with result.

    Transitions: IN_PROGRESS → COMPLETED
    """
    try:
        supabase = get_supabase_service()
        handoff_service = HandoffService(supabase)

        completion = handoff_service.complete_handoff(
            task_id=task_id,
            agent_code=request.agent_code,
            result=request.result
        )

        logger.info(
            f"Handoff {task_id} completed by {request.agent_code} | "
            f"result_keys={list(request.result.keys())}"
        )

        return HandoffCompletionResponse(
            task_id=completion.task_id,
            completed_by=completion.completed_by,
            completed_at=completion.completed_at,
            result=completion.result
        )

    except ValueError as e:
        logger.error(f"Validation error completing {task_id}: {e}")
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error completing handoff {task_id}: {e}")
        raise HTTPException(500, f"Error completing handoff: {str(e)}")
