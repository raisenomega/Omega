"""
Domain entities for Inter-Agent Handoff Protocol.
DDD: Entity layer - business logic, no dependencies on infrastructure.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class HandoffPriority(str, Enum):
    """Task priority levels"""
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class HandoffStatus(str, Enum):
    """Task lifecycle status"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class Handoff:
    """
    Represents a task handoff between two agents.

    Immutable once created (except status updates).
    """
    task_id: str
    from_agent: str
    to_agent: str
    task_type: str
    payload: Dict[str, Any]
    priority: HandoffPriority
    deadline: Optional[str]
    created_at: str
    status: HandoffStatus

    def mark_in_progress(self) -> "Handoff":
        """Transition to IN_PROGRESS status"""
        if self.status != HandoffStatus.PENDING:
            raise ValueError(f"Cannot start task in {self.status} status")
        return Handoff(
            **{**self.__dict__, "status": HandoffStatus.IN_PROGRESS}
        )

    def mark_completed(self, result: Dict[str, Any]) -> "HandoffCompletion":
        """Mark task as completed with result"""
        if self.status != HandoffStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete task in {self.status} status")
        return HandoffCompletion(
            task_id=self.task_id,
            completed_by=self.to_agent,
            completed_at=datetime.utcnow().isoformat(),
            result=result
        )

    def mark_failed(self, error: str) -> "Handoff":
        """Mark task as failed"""
        return Handoff(
            **{**self.__dict__, "status": HandoffStatus.FAILED, "error": error}
        )


@dataclass
class HandoffCompletion:
    """Represents a completed handoff with result"""
    task_id: str
    completed_by: str
    completed_at: str
    result: Dict[str, Any]


@dataclass
class HandoffConfirmation:
    """Represents agent confirmation of receipt"""
    task_id: str
    confirmed_by: str
    confirmed_at: str
    status: HandoffStatus


# DDD: Value Objects for specific handoff types
@dataclass
class ContentBriefPayload:
    """Payload for ATLAS → RAFA content briefs"""
    objective: str
    funnel_stage: str
    target_audience: str
    core_message: str
    tone: str
    format: str
    platform: str
    cta: str
    constraints: str
    success_metrics: Dict[str, Any]
    client_context_ref: str


@dataclass
class SecurityAlertPayload:
    """Payload for SENTINEL → NOVA security alerts"""
    security_score: float
    status: str
    component_scores: Dict[str, Any]
    active_alerts: list
    deploy_status: str
    recommended_actions: list
