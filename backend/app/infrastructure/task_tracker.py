"""
Task Tracker - Registers and tracks agent task execution.
DDD: Infrastructure layer. Max 200L strict.
"""
from typing import Optional
from datetime import datetime
import logging
import uuid

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class TaskTracker:
    """
    Tracks agent tasks from creation to completion.

    Records task metadata in agent_tasks table and updates
    performance metrics in omega_agents table.
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
        Create new agent task record.

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

            # Prepare task data
            task_data = {
                "id": task_id,
                "agent_code": agent_code,
                "title": title[:200],  # Truncate to DB limit
                "description": description[:1000] if description else "",
                "client_id": safe_client_id,
                "requested_by": requested_by,
                "status": "in_progress",
                "created_at": datetime.utcnow().isoformat()
            }

            # Insert task
            result = supabase.client.table("agent_tasks")\
                .insert(task_data)\
                .execute()

            if not result.data:
                raise Exception("Failed to create task - no data returned")

            logger.info(f"Task created: {task_id} for {agent_code} - {title[:50]}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to create task for {agent_code}: {e}")
            raise


    async def complete_task(
        self,
        task_id: str,
        tokens_used: int = 0,
        provider: str = "",
        model: str = ""
    ) -> bool:
        """
        Mark task as completed and update agent performance metrics.

        Args:
            task_id: Task UUID to complete
            tokens_used: Total tokens consumed
            provider: AI provider used (e.g., "openai", "anthropic")
            model: Model used (e.g., "gpt-4o-mini")

        Returns:
            True if successful, False otherwise

        Note:
            Also increments tasks_completed_total in omega_agents table
        """
        try:
            supabase = get_supabase_service()

            # Get agent_code from task
            task_resp = supabase.client.table("agent_tasks")\
                .select("agent_code")\
                .eq("id", task_id)\
                .limit(1)\
                .execute()

            if not task_resp.data:
                logger.warning(f"Task not found: {task_id}")
                return False

            agent_code = task_resp.data[0]["agent_code"]

            # Update task status
            update_data = {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "tokens_used": tokens_used,
                "provider": provider,
                "model": model
            }

            task_update = supabase.client.table("agent_tasks")\
                .update(update_data)\
                .eq("id", task_id)\
                .execute()

            if not task_update.data:
                logger.warning(f"Failed to update task: {task_id}")
                return False

            # Increment agent's completed tasks counter
            # Using PostgreSQL increment function
            agent_update = supabase.client.rpc(
                "increment_agent_tasks",
                {"agent_code_param": agent_code}
            ).execute()

            # Fallback if RPC doesn't exist: manual increment
            if not agent_update.data:
                logger.info(f"RPC not available, using fallback increment for {agent_code}")
                # Get current count
                agent_resp = supabase.client.table("omega_agents")\
                    .select("tasks_completed_total")\
                    .eq("agent_code", agent_code)\
                    .limit(1)\
                    .execute()

                if agent_resp.data:
                    current_count = agent_resp.data[0].get("tasks_completed_total", 0)
                    # Update with incremented value
                    supabase.client.table("omega_agents")\
                        .update({"tasks_completed_total": current_count + 1})\
                        .eq("agent_code", agent_code)\
                        .execute()

            logger.info(
                f"Task completed: {task_id} by {agent_code} "
                f"({tokens_used} tokens, {provider}/{model})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")
            return False
