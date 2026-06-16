"""
Task Tracker - Registers and tracks agent task execution.
DDD: Infrastructure layer. Max 200L strict.
DEBT-083: retargeted to agent_executions table for agent run telemetry.
"""
from typing import Optional
from datetime import datetime, timezone
import logging
import uuid

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class TaskTracker:
    """
    Tracks agent tasks from creation to completion.

    Records agent run telemetry in agent_executions (DEBT-083).
    """

    async def create_task(
        self,
        agent_code: str,
        title: str,
        client_id: Optional[str] = None,
        description: str = "",
        requested_by: str = "NOVA"
    ) -> str:
        """
        Create new agent execution record.

        Args:
            agent_code: Agent executing the task (e.g., "ATLAS")
            title: Task title (truncated to 200 chars)
            client_id: Optional client UUID
            description: Optional detailed description
            requested_by: Who requested the task (default: "NOVA")

        Returns:
            Task UUID

        Raises:
            Exception: If insert fails
        """
        try:
            supabase = get_supabase_service()

            # Generate task ID
            task_id = str(uuid.uuid4())

            # Guard against empty string client_id (UUID field requires valid UUID or null)
            safe_client_id = client_id if client_id and str(client_id).strip() else None

            # Prepare execution record
            execution_data = {
                "id": task_id,
                "agent_id": agent_code,
                "client_id": safe_client_id,
                "triggered_by": requested_by,
                "status": "running",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "input_data": {
                    "title": title[:200],
                    "description": description[:1000] if description else ""
                }
            }

            # Insert into agent_executions
            result = supabase.client.table("agent_executions")\
                .insert(execution_data)\
                .execute()

            if not result.data:
                raise Exception("Failed to create agent_executions record - no data returned")

            logger.info(f"agent_executions record created: {task_id} for {agent_code} - {title[:50]}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to create agent_executions record for {agent_code}: {e}")
            raise


    async def complete_task(
        self,
        task_id: str,
        tokens_used: int = 0,
        provider: str = "",
        model: str = ""
    ) -> bool:
        """
        Mark agent execution as completed.

        Args:
            task_id: Task UUID to complete
            tokens_used: Total tokens consumed
            provider: AI provider used (e.g., "anthropic")
            model: Model used (e.g., "claude-sonnet-4-6")

        Returns:
            True if successful, False otherwise
        """
        try:
            supabase = get_supabase_service()

            # Update agent_executions record to completed
            update_data = {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "output_data": {
                    "tokens_used": tokens_used,
                    "provider": provider,
                    "model": model
                }
            }

            task_update = supabase.client.table("agent_executions")\
                .update(update_data)\
                .eq("id", task_id)\
                .execute()

            if not task_update.data:
                logger.warning(f"Failed to update agent_executions record: {task_id}")
                return False

            logger.info(
                f"agent_executions record completed: {task_id} "
                f"({tokens_used} tokens, {provider}/{model})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to complete agent_executions record {task_id}: {e}")
            return False
