"""
Agent Repository
Data access layer for agents system
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
import logging

from app.domain.agents.entities import Agent, AgentExecution
from app.infrastructure.supabase_service import SupabaseService
from .agent_mapper import map_agent_to_entity, map_execution_to_entity

logger = logging.getLogger(__name__)


class AgentRepository:
    """Repository for agent data operations"""

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase

    def find_all(self) -> list[Agent]:
        """Find all active agents (DEBT-080: tabla agents no tiene department/status)"""
        query = self.supabase.client.table("agents")\
            .select("*")\
            .eq("is_active", True)\
            .order("name")
        response = query.execute()

        return [map_agent_to_entity(row) for row in response.data]

    def find_by_agent_id(self, agent_id: str) -> Optional[Agent]:
        """Find agent by its unique code (the path param is the agent code)"""
        response = self.supabase.client.table("agents")\
            .select("*")\
            .eq("code", agent_id)\
            .eq("is_active", True)\
            .single()\
            .execute()

        return map_agent_to_entity(response.data) if response.data else None

    def create_execution(self, execution: AgentExecution) -> AgentExecution:
        """Create new agent execution"""
        data = {
            "agent_id": execution.agent_id,
            "client_id": execution.client_id,
            "user_id": execution.user_id,
            "triggered_by": execution.triggered_by,
            "input_data": execution.input_data,
            "status": execution.status,
            "metadata": execution.metadata,
        }

        response = self.supabase.client.table("agent_executions").insert(data).execute()
        return map_execution_to_entity(response.data[0])

    def update_execution(self, execution: AgentExecution) -> AgentExecution:
        """Update execution status and data"""
        data = {
            "status": execution.status,
            "output_data": execution.output_data,
            "error_message": execution.error_message,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "execution_time_ms": execution.execution_time_ms,
        }

        response = self.supabase.client.table("agent_executions")\
            .update(data)\
            .eq("id", execution.id)\
            .execute()

        return map_execution_to_entity(response.data[0])

    def find_executions_by_agent(
        self,
        agent_id: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None
    ) -> list[AgentExecution]:
        """Find executions for an agent"""
        query = self.supabase.client.table("agent_executions")\
            .select("*")\
            .eq("agent_id", agent_id)\
            .eq("is_active", True)

        if status:
            query = query.eq("status", status)

        query = query.order("started_at", desc=True).range(offset, offset + limit - 1)
        response = query.execute()

        return [map_execution_to_entity(row) for row in response.data]

    def count_executions(self, agent_id: str, status: Optional[str] = None) -> int:
        """Count total executions for an agent"""
        query = self.supabase.client.table("agent_executions")\
            .select("id", count="exact")\
            .eq("agent_id", agent_id)\
            .eq("is_active", True)

        if status:
            query = query.eq("status", status)

        response = query.execute()
        return response.count if hasattr(response, 'count') else 0
