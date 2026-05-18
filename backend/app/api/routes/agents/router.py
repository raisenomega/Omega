"""
Agents Router
FastAPI REST endpoints for agents system
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

from .models import ExecuteAgentRequest, ExecutionResponse
from .handlers import handle_execute_agent
from .handlers.execute_agent_agentic import handle_execute_agent_agentic

router = APIRouter(prefix="/agents", tags=["Agents 🤖"])


@router.post("/{agent_id}/execute/", response_model=ExecutionResponse, status_code=201)
async def execute_agent(
    agent_id: str = Path(..., description="Agent identifier"),
    request: ExecuteAgentRequest = ...
) -> ExecutionResponse:
    """
    Execute an agent

    Triggers agent execution with provided input data.
    Returns execution details including status and output.

    **Note**: Agent must be in 'active' status to execute.
    """
    return await handle_execute_agent(agent_id, request)


@router.post("/{agent_id}/execute-agentic/", response_model=ExecutionResponse)
async def execute_agent_agentic(
    agent_id: str = Path(..., description="Agent identifier"),
    request: ExecuteAgentRequest = ...
):
    """
    Execute an agent with AgenticRunner (Agentic Loop v2)

    Uses real tools: web_search, fetch_url, supabase_read/write.
    Same contract as /execute/ but with agentic loop and tool calling.

    **New Features**:
    - Real-time web search via Tavily API
    - URL content extraction with domain blocking
    - Database operations with tenant isolation
    - Input injection detection + output filtering
    - Multi-iteration reasoning (max 10)

    **Note**: Agent must be in 'active' status to execute.
    """
    result = await handle_execute_agent_agentic(agent_id, request)
    return JSONResponse(
        content=result.model_dump(),
        status_code=201,
        media_type="application/json; charset=utf-8"
    )
