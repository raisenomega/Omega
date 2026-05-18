"""
Orchestrator Agent
Routes execution between agents and manages agent chains
Filosofía: No velocity, only precision 🐢💎
"""
import logging
from typing import Optional
from datetime import datetime

from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.client_context_repository import ClientContextRepository
from app.infrastructure.repositories.agent_repository import AgentRepository
from app.domain.agents.entities import AgentExecution
from .client_context_agent import ClientContextAgent

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    """Orchestrates agent execution chains with shared context"""

    CHAINS = {
        "content_generation": ["client_context", "content_creator"],
        "hashtag_generation": ["client_context", "hashtag_generator"],
        "brand_analysis": ["client_context", "brand_voice"],
        "full_analysis": ["client_context", "competitive_intelligence", "trend_hunter"],
    }

    def __init__(self, lazy: bool = False):
        if not lazy:
            self.supabase = get_supabase_service()
            self.context_repo = ClientContextRepository(self.supabase)
            self.agent_repo = AgentRepository(self.supabase)
            self.client_context_agent = ClientContextAgent()
        else:
            self.supabase = None
            self.context_repo = None
            self.agent_repo = None
            self.client_context_agent = None

    def _ensure_initialized(self):
        """Initialize connections if not already initialized"""
        if self.supabase is None:
            self.supabase = get_supabase_service()
            self.context_repo = ClientContextRepository(self.supabase)
            self.agent_repo = AgentRepository(self.supabase)
            self.client_context_agent = ClientContextAgent()

    async def route(self, trigger: str, client_id: str, input_data: dict) -> dict:
        """Route execution through agent chain"""
        self._ensure_initialized()
        try:
            # Validate chain exists
            if trigger not in self.CHAINS:
                return {
                    "error": f"Unknown trigger: {trigger}",
                    "available_triggers": list(self.CHAINS.keys())
                }

            chain = self.CHAINS[trigger]
            logger.info(f"Orchestrator: Starting chain '{trigger}' for client {client_id}")

            # Execute chain
            result = await self._execute_chain(chain, client_id, input_data)

            return {
                "trigger": trigger,
                "chain": chain,
                "client_id": client_id,
                "result": result,
                "message": f"Chain '{trigger}' executed successfully"
            }

        except Exception as e:
            logger.error(f"Orchestrator chain failed: {e}")
            return {
                "error": str(e),
                "trigger": trigger,
                "client_id": client_id
            }

    async def _execute_chain(self, chain: list[str], client_id: str, input_data: dict) -> dict:
        """Execute agent chain sequentially"""
        context_data = None
        outputs = {}

        for agent_id in chain:
            logger.info(f"Orchestrator: Executing {agent_id}")

            # Special handling for client_context agent
            if agent_id == "client_context":
                context_data = await self.client_context_agent.execute(client_id)
                outputs[agent_id] = context_data
                continue

            # Load context for subsequent agents
            enriched_input = await self._enrich_input(client_id, input_data)

            # Record execution
            execution = await self._create_execution(agent_id, client_id, enriched_input)

            # Execute agent (placeholder - real agents would be imported)
            output = await self._execute_agent(agent_id, enriched_input)

            # Update execution record
            await self._complete_execution(execution, output)

            outputs[agent_id] = output

        return outputs

    async def _enrich_input(self, client_id: str, input_data: dict) -> dict:
        """Enrich input with client context"""
        context = self.context_repo.find_by_client_id(client_id)

        enriched = input_data.copy()
        if context and context.has_context():
            enriched["client_context"] = {
                "niche": context.niche,
                "tone": context.tone,
                "brand_voice": context.brand_voice,
                "target_audience": context.target_audience,
                "content_themes": context.content_themes,
                "preferred_formats": context.preferred_formats,
            }

        return enriched

    async def _create_execution(self, agent_id: str, client_id: str, input_data: dict) -> AgentExecution:
        """Create execution record"""
        execution = AgentExecution(
            agent_id=agent_id,
            client_id=client_id,
            triggered_by="orchestrator",
            input_data=input_data,
            status="pending",
        )

        return self.agent_repo.create_execution(execution)

    async def _execute_agent(self, agent_id: str, input_data: dict) -> dict:
        """
        Execute specific agent (mock for now)
        In production, this would dynamically import and call the agent
        """
        # Mock execution - return enriched input to show context passing works
        return {
            "agent_id": agent_id,
            "status": "executed",
            "input_received": input_data,
            "message": f"Agent {agent_id} executed with context"
        }

    async def _complete_execution(self, execution: AgentExecution, output: dict) -> None:
        """Update execution with results"""
        execution.mark_as_completed(output)
        self.agent_repo.update_execution(execution)

    def get_available_chains(self) -> dict:
        """Return available execution chains"""
        descs = {
            "content_generation": "Analyze client context and generate personalized content",
            "hashtag_generation": "Generate hashtags based on client's niche and trends",
            "brand_analysis": "Analyze and maintain brand voice consistency",
            "full_analysis": "Complete analysis: context, competition, and trends"
        }
        return {
            trigger: {"agents": chain, "description": descs.get(trigger, "No description")}
            for trigger, chain in self.CHAINS.items()
        }

    async def execute(self, params: dict) -> dict:
        """
        Execute orchestrator action (compatibility method for orchestrator router)
        """
        action_type = params.get("type", "route")

        if action_type == "route" or action_type == "execute_workflow":
            trigger = params.get("workflow_name") or params.get("trigger", "content_generation")
            client_id = params.get("client_id")
            input_data = params.get("params", {})
            return await self.route(trigger, client_id, input_data)

        return {"status": "not_implemented", "action": action_type}

    def get_status(self) -> dict:
        """Get orchestrator agent status"""
        return {
            "agent": "orchestrator",
            "status": "active",
            "available_chains": list(self.CHAINS.keys())
        }


# Export singleton instance with lazy initialization to prevent blocking imports
orchestrator_agent = OrchestratorAgent(lazy=True)
