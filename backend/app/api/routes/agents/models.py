"""
Agent API Models
Pydantic DTOs for request/response validation
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.domain.agents.types import AgentStatusType, ExecutionStatusType, LogLevelType


class AgentResponse(BaseModel):
    """DTO for agent response"""
    id: str
    agent_id: str
    name: str
    description: Optional[str] = None
    department: str
    category: Optional[str] = None
    status: AgentStatusType
    version: str
    capabilities: List[str]
    config: dict[str, Any]
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_execution_time_ms: float
    last_executed_at: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class AgentListResponse(BaseModel):
    """DTO for list of agents"""
    items: List[AgentResponse]
    total: int
    department_filter: Optional[str] = None
    status_filter: Optional[str] = None


class AgentDetailResponse(BaseModel):
    """DTO for agent detail with stats"""
    agent: AgentResponse
    stats: dict[str, Any]


class ExecuteAgentRequest(BaseModel):
    """DTO for executing an agent"""
    input_data: dict[str, Any] = Field(..., description="Input data for agent execution")
    client_id: Optional[str] = Field(None, description="Client context UUID")
    user_id: Optional[str] = Field(None, description="User context UUID")
    triggered_by: str = Field(default="api", description="Execution trigger source")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "input_data": {"content": "Sample post", "platform": "instagram"},
                "client_id": "bd68ca50-b8ef-4240-a0ce-44df58f53171",
                "triggered_by": "api"
            }
        }


class ExecutionResponse(BaseModel):
    """DTO for execution response"""
    id: str
    agent_id: str
    client_id: Optional[str] = None
    user_id: Optional[str] = None
    triggered_by: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    error_message: Optional[str] = None
    status: ExecutionStatusType
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_ms: Optional[int] = None
    metadata: dict[str, Any]
    created_at: str


class ExecutionListResponse(BaseModel):
    """DTO for list of executions"""
    items: List[ExecutionResponse]
    total: int
    limit: int
    offset: int
    agent_id: str


class LogResponse(BaseModel):
    """DTO for log entry"""
    id: str
    execution_id: str
    agent_id: str
    level: LogLevelType
    message: str
    details: dict[str, Any]
    logged_at: str
    created_at: str


class LogListResponse(BaseModel):
    """DTO for list of logs"""
    items: List[LogResponse]
    total: int
    execution_id: str
