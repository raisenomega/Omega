"""
Inter-Agent Handoff Service — Structured task delegation protocol.
DDD: Application Service layer - orchestrates domain entities.
Strict <200L per file.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import logging
from app.domain.handoff.entities import (
    Handoff,
    HandoffPriority,
    HandoffStatus,
    HandoffConfirmation,
    HandoffCompletion
)
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class HandoffService:
    """
    Orchestrates task delegation between agents.

    Protocol:
    1. create_handoff() → stores task in omega_agent_memory
    2. confirm_receipt() → agent acknowledges
    3. complete_handoff() → agent delivers result
    """

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase

    def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: str = "NORMAL",
        deadline: Optional[str] = None
    ) -> Handoff:
        """
        Creates structured handoff between agents.

        Args:
            from_agent: Source agent code (e.g., "NOVA")
            to_agent: Target agent code (e.g., "ATLAS")
            task_type: Type of task ("content_brief", "security_alert", etc.)
            payload: Task-specific data
            priority: URGENT | HIGH | NORMAL | LOW
            deadline: ISO8601 timestamp (optional)

        Returns:
            Handoff entity with task_id for tracking
        """
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"

        handoff = Handoff(
            task_id=task_id,
            from_agent=from_agent,
            to_agent=to_agent,
            task_type=task_type,
            payload=payload,
            priority=HandoffPriority(priority),
            deadline=deadline,
            created_at=datetime.utcnow().isoformat(),
            status=HandoffStatus.PENDING
        )

        # Store in omega_agent_memory as "handoff" type
        self._store_handoff(handoff)

        logger.info(
            f"Handoff created: {task_id} | {from_agent} → {to_agent} | "
            f"type={task_type}, priority={priority}"
        )

        return handoff

    def confirm_receipt(self, task_id: str, agent_code: str) -> HandoffConfirmation:
        """
        Agent confirms receipt of handoff.

        Transitions task to IN_PROGRESS.
        """
        handoff = self._get_handoff(task_id)

        if handoff.to_agent != agent_code:
            raise ValueError(
                f"Agent {agent_code} cannot confirm task for {handoff.to_agent}"
            )

        updated_handoff = handoff.mark_in_progress()
        self._update_handoff(updated_handoff)

        confirmation = HandoffConfirmation(
            task_id=task_id,
            confirmed_by=agent_code,
            confirmed_at=datetime.utcnow().isoformat(),
            status=HandoffStatus.IN_PROGRESS
        )

        logger.info(f"Handoff {task_id} confirmed by {agent_code}")

        return confirmation

    def complete_handoff(
        self,
        task_id: str,
        agent_code: str,
        result: Dict[str, Any]
    ) -> HandoffCompletion:
        """
        Agent marks handoff as complete with result.

        Transitions task to COMPLETED.
        """
        handoff = self._get_handoff(task_id)

        if handoff.to_agent != agent_code:
            raise ValueError(
                f"Agent {agent_code} cannot complete task for {handoff.to_agent}"
            )

        completion = handoff.mark_completed(result)

        # Update status in storage
        completed_handoff = Handoff(
            **{**handoff.__dict__, "status": HandoffStatus.COMPLETED}
        )
        self._update_handoff(completed_handoff)

        # Store completion result
        self._store_completion(completion)

        logger.info(
            f"Handoff {task_id} completed by {agent_code}"
        )

        return completion

    def get_pending_handoffs(self, agent_code: str) -> list[Handoff]:
        """Get all pending handoffs for an agent"""
        response = self.supabase.client.table("omega_agent_memory").select(
            "content"
        ).eq("agent_code", agent_code).eq(
            "memory_type", "handoff"
        ).execute()

        handoffs = []
        for row in response.data:
            content = row["content"]
            if content.get("status") == "PENDING":
                handoffs.append(Handoff(**content))

        return handoffs

    # Private methods for storage (infrastructure layer)
    def _store_handoff(self, handoff: Handoff) -> None:
        """Store handoff in omega_agent_memory"""
        self.supabase.client.table("omega_agent_memory").insert({
            "agent_code": handoff.to_agent,
            "memory_type": "handoff",
            "content": handoff.__dict__,
            "priority": handoff.priority.value,
            "expires_at": handoff.deadline
        }).execute()

    def _update_handoff(self, handoff: Handoff) -> None:
        """Update handoff status"""
        self.supabase.client.table("omega_agent_memory").update({
            "content": handoff.__dict__
        }).eq("agent_code", handoff.to_agent).eq(
            "memory_type", "handoff"
        ).match({"content->>task_id": handoff.task_id}).execute()

    def _get_handoff(self, task_id: str) -> Handoff:
        """Retrieve handoff by task_id"""
        response = self.supabase.client.table("omega_agent_memory").select(
            "content"
        ).eq("memory_type", "handoff").match(
            {"content->>task_id": task_id}
        ).execute()

        if not response.data:
            raise ValueError(f"Handoff {task_id} not found")

        return Handoff(**response.data[0]["content"])

    def _store_completion(self, completion: HandoffCompletion) -> None:
        """Store completion result"""
        self.supabase.client.table("omega_agent_memory").insert({
            "agent_code": completion.completed_by,
            "memory_type": "handoff_completion",
            "content": completion.__dict__
        }).execute()
