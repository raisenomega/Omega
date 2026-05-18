"""
Orchestrator API Routes
Endpoints for workflow coordination and system monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from app.agents.orchestrator_agent import orchestrator_agent

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])


# Request Models
class ExecuteWorkflowRequest(BaseModel):
    """Request for workflow execution"""
    workflow_name: str = Field(..., description="Workflow name")
    client_id: str = Field(..., description="Client ID")
    params: dict[str, str | int | List] = Field(..., description="Workflow parameters")


class RouteTaskRequest(BaseModel):
    """Request for task routing"""
    task_type: str = Field(..., description="Task type")
    payload: dict[str, str | int | List | Dict] = Field(..., description="Task payload")


class PauseWorkflowRequest(BaseModel):
    """Request for pausing workflow"""
    workflow_id: str = Field(..., description="Workflow ID")
    reason: str = Field(..., description="Reason for pause")


# Response Model
class OrchestratorAPIResponse(BaseModel):
    """Generic orchestrator response"""
    success: bool
    data: dict
    message: str | None = None


@router.post("/execute-workflow", response_model=OrchestratorAPIResponse)
async def execute_workflow(
    request: ExecuteWorkflowRequest
) -> OrchestratorAPIResponse:
    """
    Execute complete workflow coordinating multiple agents

    - **workflow_name**: Name of workflow to execute
      - full_content_pipeline: Brief → Content → Brand Voice → Scheduling
      - crisis_response: Detection → Crisis Manager → Engagement → Monitor
      - weekly_client_report: Analytics → Growth → Report
      - trend_to_content: Trend Hunter → Strategy → Content → Brand → Schedule
      - competitive_analysis: Competitive Intel → Analytics → Strategy → Report
    - **client_id**: Client identifier
    - **params**: Workflow parameters

    Returns workflow execution with steps and progress
    """
    try:
        result = await orchestrator_agent.execute({
            "type": "execute_workflow",
            "workflow_name": request.workflow_name,
            "client_id": request.client_id,
            "params": request.params
        })

        return OrchestratorAPIResponse(
            success=True,
            data=result,
            message=f"Workflow {request.workflow_name} started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route-task", response_model=OrchestratorAPIResponse)
async def route_task(
    request: RouteTaskRequest
) -> OrchestratorAPIResponse:
    """
    Route task to correct agent automatically

    - **task_type**: Type of task (generate_content, validate_brand_voice, etc.)
    - **payload**: Task payload with parameters

    Returns routed task with assigned agent
    """
    try:
        result = await orchestrator_agent.execute({
            "type": "route_task",
            "task_type": request.task_type,
            "payload": request.payload
        })

        return OrchestratorAPIResponse(
            success=True,
            data=result,
            message=f"Task routed to {result.get('assigned_agent', 'unknown')}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-state", response_model=OrchestratorAPIResponse)
async def get_system_state() -> OrchestratorAPIResponse:
    """
    Get complete system state in real-time

    Returns:
    - Active workflows count
    - Queued tasks count
    - Online agents count
    - Agent statuses
    - System load (0.0 to 1.0)
    - Last health check timestamp
    """
    try:
        result = await orchestrator_agent.execute({
            "type": "get_system_state"
        })

        return OrchestratorAPIResponse(
            success=True,
            data=result,
            message="System state retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}", response_model=OrchestratorAPIResponse)
async def get_workflow_status(
    workflow_id: str
) -> OrchestratorAPIResponse:
    """
    Get current status of specific workflow

    - **workflow_id**: Workflow identifier

    Returns workflow status with completed steps and progress
    """
    try:
        result = await orchestrator_agent.execute({
            "type": "get_workflow_status",
            "workflow_id": workflow_id
        })

        return OrchestratorAPIResponse(
            success=True,
            data=result,
            message="Workflow status retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause-workflow", response_model=OrchestratorAPIResponse)
async def pause_workflow(
    request: PauseWorkflowRequest
) -> OrchestratorAPIResponse:
    """
    Pause workflow (useful for human approval)

    - **workflow_id**: Workflow to pause
    - **reason**: Reason for pausing

    Returns paused workflow
    """
    try:
        result = await orchestrator_agent.execute({
            "type": "pause_workflow",
            "workflow_id": request.workflow_id,
            "reason": request.reason
        })

        return OrchestratorAPIResponse(
            success=True,
            data=result,
            message=f"Workflow {request.workflow_id} paused: {request.reason}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Orchestrator Agent status"""
    return orchestrator_agent.get_status()
