"""
Agent Execution Helpers
Helper functions for agent execution and context management
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.agents.models import ExecuteAgentRequest
from app.domain.agents.context_entity import ClientContext
from app.infrastructure.repositories.client_context_repository import ClientContextRepository

logger = logging.getLogger(__name__)


async def save_to_client_context(
    supabase,
    agent_id: str,
    client_id: str,
    output: dict
) -> None:
    """Save agent output to client_context for shared learning"""
    try:
        context_repo = ClientContextRepository(supabase)
        context = context_repo.find_by_client_id(client_id)

        if not context:
            context = ClientContext(client_id=client_id)

        # Update context based on agent type
        if agent_id == "analytics":
            context.update_analytics(
                engagement_rate=output.get("avg_engagement_rate"),
                peak_hours=output.get("peak_posting_hours"),
                hashtags=output.get("top_hashtags"),
                demographics=output.get("demographics")
            )
        elif agent_id == "brand_voice":
            context.update_brand_voice(agent_id, output.get("brand_voice", {}))
            if output.get("tone"):
                context.tone = output.get("tone")
        elif agent_id == "competitive_intelligence":
            competitors = output.get("competitors", [])
            for comp in competitors:
                context.add_competitor(comp)
        elif agent_id == "trend_hunter":
            if output.get("top_hashtags"):
                context.top_hashtags = output.get("top_hashtags", [])[:30]
            if output.get("content_themes"):
                context.content_themes = output.get("content_themes", [])
        elif agent_id == "audience_insights":
            context.audience_demographics = output.get("demographics", {})
            if output.get("target_audience"):
                context.target_audience = output.get("target_audience")

        context.last_updated_by = agent_id
        context_repo.upsert(context)
        logger.info(f"Saved {agent_id} output to client_context for client {client_id}")

    except Exception as e:
        logger.warning(f"Failed to save to client_context: {e}")


async def execute_special_agent(agent_id: str, request: ExecuteAgentRequest) -> dict:
    """Execute special agents: orchestrator and client_context"""
    if agent_id == "client_context":
        from app.agents.client_context_agent import ClientContextAgent
        if not request.client_id:
            raise HTTPException(400, "client_id required for ClientContextAgent")

        agent = ClientContextAgent()
        return await agent.execute(request.client_id)

    elif agent_id == "orchestrator":
        from app.agents.orchestrator_agent import OrchestratorAgent
        if not request.client_id:
            raise HTTPException(400, "client_id required for OrchestratorAgent")

        trigger = request.input_data.get("trigger", "content_generation")
        agent = OrchestratorAgent()
        return await agent.route(trigger, request.client_id, request.input_data)

    return {"error": "Unknown special agent"}
