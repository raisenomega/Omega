"""
Handoff API Models — Request/Response schemas for inter-agent handoff protocol.
DDD: API Interface layer - contracts for external communication.
Strict <200L per file.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class HandoffCreateRequest(BaseModel):
    """Request to create a new handoff between agents"""
    from_agent: str = Field(..., description="Source agent code (e.g., 'NOVA')")
    to_agent: str = Field(..., description="Target agent code (e.g., 'ATLAS')")
    task_type: str = Field(..., description="Type of task: content_brief, security_alert, churn_intervention, etc.")
    payload: Dict[str, Any] = Field(..., description="Task-specific data")
    priority: str = Field(default="NORMAL", description="URGENT | HIGH | NORMAL | LOW")
    deadline: Optional[str] = Field(None, description="ISO8601 deadline (optional)")

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        """Convert priority to uppercase to accept 'high' or 'HIGH'"""
        if isinstance(v, str):
            return v.upper()
        return v

    class Config:
        schema_extra = {
            "example": {
                "from_agent": "NOVA",
                "to_agent": "ATLAS",
                "task_type": "content_brief",
                "payload": {
                    "objective": "Generate LinkedIn content series",
                    "funnel_stage": "awareness",
                    "target_audience": "Software engineers",
                    "core_message": "AI-powered development tools"
                },
                "priority": "HIGH",
                "deadline": "2026-03-01T23:59:59Z"
            }
        }


class HandoffConfirmRequest(BaseModel):
    """Request to confirm receipt of handoff"""
    agent_code: str = Field(..., description="Agent code confirming the task")

    class Config:
        schema_extra = {
            "example": {
                "agent_code": "ATLAS"
            }
        }


class HandoffCompleteRequest(BaseModel):
    """Request to mark handoff as complete with result"""
    agent_code: str = Field(..., description="Agent code completing the task")
    result: Dict[str, Any] = Field(..., description="Task result data")

    class Config:
        schema_extra = {
            "example": {
                "agent_code": "RAFA",
                "result": {
                    "content_generated": 5,
                    "posts": [
                        {"platform": "LinkedIn", "content": "Post content here..."},
                        {"platform": "Twitter", "content": "Tweet content..."}
                    ],
                    "performance_forecast": {
                        "estimated_engagement": 0.045,
                        "reach_projection": 2500
                    }
                }
            }
        }


class HandoffResponse(BaseModel):
    """Standard handoff response"""
    task_id: str
    from_agent: str
    to_agent: str
    task_type: str
    payload: Dict[str, Any]
    priority: str
    status: str
    created_at: str
    deadline: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "task_id": "TASK-a3f7c8d9",
                "from_agent": "NOVA",
                "to_agent": "ATLAS",
                "task_type": "content_brief",
                "payload": {"objective": "Generate content series"},
                "priority": "HIGH",
                "status": "PENDING",
                "created_at": "2026-02-24T10:30:00Z",
                "deadline": "2026-03-01T23:59:59Z"
            }
        }


class HandoffConfirmationResponse(BaseModel):
    """Response after confirming handoff receipt"""
    task_id: str
    confirmed_by: str
    confirmed_at: str
    status: str

    class Config:
        schema_extra = {
            "example": {
                "task_id": "TASK-a3f7c8d9",
                "confirmed_by": "ATLAS",
                "confirmed_at": "2026-02-24T10:35:00Z",
                "status": "IN_PROGRESS"
            }
        }


class HandoffCompletionResponse(BaseModel):
    """Response after completing handoff"""
    task_id: str
    completed_by: str
    completed_at: str
    result: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "task_id": "TASK-a3f7c8d9",
                "completed_by": "RAFA",
                "completed_at": "2026-02-24T15:00:00Z",
                "result": {
                    "content_generated": 5,
                    "status": "success"
                }
            }
        }


class HandoffListResponse(BaseModel):
    """Response for listing handoffs"""
    handoffs: List[HandoffResponse]
    count: int

    class Config:
        schema_extra = {
            "example": {
                "handoffs": [
                    {
                        "task_id": "TASK-a3f7c8d9",
                        "from_agent": "NOVA",
                        "to_agent": "ATLAS",
                        "task_type": "content_brief",
                        "payload": {},
                        "priority": "HIGH",
                        "status": "PENDING",
                        "created_at": "2026-02-24T10:30:00Z"
                    }
                ],
                "count": 1
            }
        }
