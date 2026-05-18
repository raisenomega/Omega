"""
Handoff API Router — Thin delegation layer to handlers.
Filosofía: No velocity, only precision 🐢💎
DDD: API Interface layer - HTTP routing only.
Strict <200L per file.
"""
from fastapi import APIRouter
from .models import (
    HandoffCreateRequest,
    HandoffConfirmRequest,
    HandoffCompleteRequest,
    HandoffResponse,
    HandoffConfirmationResponse,
    HandoffCompletionResponse,
    HandoffListResponse
)
from .handlers import (
    handle_create_handoff,
    handle_confirm_handoff,
    handle_complete_handoff,
    handle_get_pending,
    handle_get_handoff
)

router = APIRouter(prefix="/handoff", tags=["handoff"])


@router.post("/", response_model=HandoffResponse, status_code=201)
async def create_handoff(request: HandoffCreateRequest):
    """Creates structured handoff between agents"""
    return await handle_create_handoff(request)


@router.post("/{task_id}/confirm", response_model=HandoffConfirmationResponse)
async def confirm_handoff(task_id: str, request: HandoffConfirmRequest):
    """Agent confirms receipt of handoff (PENDING → IN_PROGRESS)"""
    return await handle_confirm_handoff(task_id, request)


@router.post("/{task_id}/complete", response_model=HandoffCompletionResponse)
async def complete_handoff(task_id: str, request: HandoffCompleteRequest):
    """Agent marks handoff as complete (IN_PROGRESS → COMPLETED)"""
    return await handle_complete_handoff(task_id, request)


@router.get("/pending/{agent_code}", response_model=HandoffListResponse)
async def get_pending_handoffs(agent_code: str):
    """Retrieves all pending handoffs for an agent"""
    return await handle_get_pending(agent_code)


@router.get("/{task_id}", response_model=HandoffResponse)
async def get_handoff(task_id: str):
    """Retrieves a specific handoff by task_id"""
    return await handle_get_handoff(task_id)
