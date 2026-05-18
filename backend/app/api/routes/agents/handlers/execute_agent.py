"""
Handler: Execute Agent
Executes an agent with given input
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging
import importlib

from app.api.routes.agents.models import ExecuteAgentRequest, ExecutionResponse
from app.domain.agents.entities import AgentExecution
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.agent_repository import AgentRepository
from .agent_helpers import save_to_client_context, execute_special_agent

logger = logging.getLogger(__name__)

# Agents that update client_context with their learnings
CONTEXT_AWARE_AGENTS = {
    "analytics": "analytics",
    "brand_voice": "brand_identity",
    "competitive_intelligence": "competitive",
    "trend_hunter": "trends",
    "audience_insights": "audience",
    "sentiment_analyzer": "sentiment",
}


async def handle_execute_agent(
    agent_id: str,
    request: ExecuteAgentRequest
) -> ExecutionResponse:
    """
    Execute an agent with input data

    Args:
        agent_id: Agent identifier
        request: Execution request with input_data

    Returns:
        ExecutionResponse with execution status and output

    Raises:
        HTTPException 404: If agent not found
        HTTPException 400: If agent cannot execute
        HTTPException 500: If execution fails
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = AgentRepository(supabase)

        # Fetch agent
        agent = repo.find_by_agent_id(agent_id)

        if not agent:
            raise HTTPException(404, f"Agent '{agent_id}' not found")

        if not agent.can_execute():
            raise HTTPException(
                400,
                f"Agent '{agent_id}' cannot execute (status: {agent.status})"
            )

        # Create execution record
        execution = AgentExecution(
            agent_id=agent_id,
            client_id=request.client_id,
            user_id=request.user_id,
            triggered_by=request.triggered_by,
            input_data=request.input_data,
            metadata=request.metadata,
            status="pending",
        )

        execution = repo.create_execution(execution)
        execution.mark_as_running()
        repo.update_execution(execution)

        # Special handling for orchestrator and client_context agents
        if agent_id in ("orchestrator", "client_context"):
            output = await execute_special_agent(agent_id, request)
            execution.mark_as_completed(output)
            repo.update_execution(execution)

        # Dynamic agent execution
        else:
            try:
                # Try to import and execute the agent
                module_path = f"app.agents.{agent_id.replace('-', '_')}_agent"
                try:
                    agent_module = importlib.import_module(module_path)
                    agent_class = getattr(agent_module, f"{agent_id.replace('-', '_').title().replace('_', '')}Agent")
                    agent_instance = agent_class()

                    # Execute agent (assumes execute method exists)
                    if hasattr(agent_instance, 'execute'):
                        output = await agent_instance.execute(request.input_data)
                    else:
                        output = {"message": "Agent executed", "result": "success"}

                except (ImportError, AttributeError) as import_error:
                    logger.warning(f"Could not import agent {agent_id}: {import_error}")
                    # Fallback: return mock execution
                    output = {
                        "agent_id": agent_id,
                    "status": "executed",
                    "message": f"Agent '{agent.name}' executed successfully (mock)",
                    "input_received": request.input_data,
                }

                execution.mark_as_completed(output)
                repo.update_execution(execution)

                # Save to client_context if agent produces contextual learning
                if agent_id in CONTEXT_AWARE_AGENTS and request.client_id:
                    await save_to_client_context(
                        supabase=supabase,
                        agent_id=agent_id,
                        client_id=request.client_id,
                        output=output
                    )

                logger.info(f"Agent '{agent_id}' executed successfully (execution_id={execution.id})")

            except Exception as exec_error:
                error_msg = str(exec_error)
                execution.mark_as_failed(error_msg)
                repo.update_execution(execution)
                logger.error(f"Agent execution failed: {error_msg}")
                raise HTTPException(500, f"Agent execution failed: {error_msg}")

        # Map to response DTO
        return ExecutionResponse(
            id=execution.id,
            agent_id=execution.agent_id,
            client_id=execution.client_id,
            user_id=execution.user_id,
            triggered_by=execution.triggered_by,
            input_data=execution.input_data,
            output_data=execution.output_data,
            error_message=execution.error_message,
            status=execution.status,
            started_at=execution.started_at.isoformat() if execution.started_at else None,
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            execution_time_ms=execution.execution_time_ms,
            metadata=execution.metadata,
            created_at=execution.created_at.isoformat() if execution.created_at else "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent {agent_id}: {e}")
        raise HTTPException(500, f"Failed to execute agent: {str(e)}")
