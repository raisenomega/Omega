"""
Agent Domain Entities
Business entities for agents system
Filosofía: No velocity, only precision 🐢💎
"""
from datetime import datetime
from typing import Optional, Any
from dataclasses import dataclass, field

from .types import AgentStatusType, ExecutionStatusType, LogLevelType


@dataclass
class Agent:
    """
    Agent Entity

    Represents an AI agent in the system with capabilities and configuration.
    """
    # Identity
    id: Optional[str] = None
    agent_id: str = ""
    name: str = ""
    description: Optional[str] = None

    # Classification
    department: str = ""
    category: Optional[str] = None
    status: AgentStatusType = "active"
    version: str = "1.0.0"

    # Capabilities
    capabilities: list[str] = field(default_factory=list)
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)

    # Configuration
    config: dict[str, Any] = field(default_factory=dict)
    max_execution_time_seconds: int = 300
    retry_policy: dict[str, Any] = field(default_factory=lambda: {"max_retries": 3, "backoff_multiplier": 2})

    # Metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time_ms: float = 0.0
    last_executed_at: Optional[datetime] = None

    # Metadata
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_operational(self) -> bool:
        """Check if agent is operational"""
        return self.status == "active" and self.is_active

    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100

    def can_execute(self) -> bool:
        """Check if agent can execute tasks"""
        return self.is_operational() and self.status != "maintenance"

    def update_metrics(self, success: bool, execution_time_ms: int) -> None:
        """Update agent metrics after execution"""
        self.total_executions += 1
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1

        # Update average execution time
        if self.avg_execution_time_ms == 0:
            self.avg_execution_time_ms = execution_time_ms
        else:
            self.avg_execution_time_ms = (
                (self.avg_execution_time_ms * (self.total_executions - 1) + execution_time_ms)
                / self.total_executions
            )

        self.last_executed_at = datetime.utcnow()


@dataclass
class AgentExecution:
    """
    Agent Execution Entity

    Tracks individual agent execution runs with input/output data.
    """
    # Identity
    id: Optional[str] = None
    agent_id: str = ""

    # Context
    client_id: Optional[str] = None
    user_id: Optional[str] = None
    triggered_by: str = "manual"

    # Data
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    # Status
    status: ExecutionStatusType = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: Optional[datetime] = None

    def is_running(self) -> bool:
        """Check if execution is currently running"""
        return self.status == "running"

    def is_completed(self) -> bool:
        """Check if execution completed successfully"""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """Check if execution failed"""
        return self.status == "failed"

    def mark_as_running(self) -> None:
        """Start execution"""
        self.status = "running"
        self.started_at = datetime.utcnow()

    def mark_as_completed(self, output: dict[str, Any]) -> None:
        """Complete execution successfully"""
        self.status = "completed"
        self.output_data = output
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.execution_time_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)

    def mark_as_failed(self, error: str) -> None:
        """Mark execution as failed"""
        self.status = "failed"
        self.error_message = error
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.execution_time_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)


@dataclass
class AgentLog:
    """
    Agent Log Entity

    Detailed log entry for debugging agent executions.
    """
    # Identity
    id: Optional[str] = None
    execution_id: str = ""
    agent_id: str = ""

    # Log details
    level: LogLevelType = "info"
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    # Timestamp
    logged_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def is_error(self) -> bool:
        """Check if log is error level or higher"""
        return self.level in ["error", "critical"]
