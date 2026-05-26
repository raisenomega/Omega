"""
Agent Routing Helper - Detects agent mentions and routes to dispatcher.
DDD: Application layer helper. Max 200L strict.
"""
from typing import Optional, List, Dict, Any
import re
import logging
from app.infrastructure.ai.agent_dispatcher import AgentDispatcher
from app.infrastructure.ai.providers import ChatMessage, MessageRole
from app.infrastructure.task_tracker import TaskTracker

logger = logging.getLogger(__name__)

# Agents that can be directly invoked via mentions
ROUTABLE_AGENTS = [
    "ATLAS", "PIXEL", "DUDA", "RAFA", "ECHO", "LUAN",  # Marketing
    "LUNA", "SHIELD", "FORGE", "DEBUG", "SCOPE",  # Product
    "REX", "ANCHOR", "BRIDGE", "FLOW", "SCOUT",  # Operations
    "VERA", "LEDGER", "PULSE_FIN", "QUOTA", "MARGIN",  # Finance
    "KIRA", "REVIEW", "NURTURE", "TRIBE", "VOICE",  # Community
    "ORACLE", "TREND", "SIGNAL", "MAP", "LENS",  # Intelligence
    "SOPHIA", "HIRE", "TRAIN", "CULTURE", "COMPASS",  # People
    "SENTINEL", "VAULT", "PULSE_MON", "GUARD"  # Security (partial)
]


def detect_agent_mention(message_content: str) -> Optional[str]:
    """
    Detect if message mentions an agent explicitly.

    Looks for patterns like "ATLAS:", "@PIXEL", "DUDA:"

    Args:
        message_content: User message text

    Returns:
        Agent code if detected, None otherwise
    """
    # Pattern: Agent name followed by colon or preceded by @
    pattern = r"(?:^|\s)(?:@)?(" + "|".join(ROUTABLE_AGENTS) + r")(?::|\s|$)"
    match = re.search(pattern, message_content, re.IGNORECASE)

    if match:
        agent_code = match.group(1).upper()
        logger.info(f"Detected agent mention: {agent_code}")
        return agent_code

    return None


async def route_to_agent(
    agent_code: str,
    messages: List[Dict[str, str]],
    system_prompt: str,
    max_tokens: int = 4096,
    client_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Route request to specific agent via dispatcher.

    Args:
        agent_code: Agent to route to (e.g., "ATLAS")
        messages: Chat messages (dict format)
        system_prompt: System prompt for context
        max_tokens: Max tokens

    Returns:
        Dict with agent response

    Raises:
        Exception: If dispatch fails
    """
    dispatcher = AgentDispatcher()
    tracker = TaskTracker()

    # Convert dict messages to ChatMessage objects
    chat_messages: List[ChatMessage] = []
    for msg in messages:
        role = MessageRole(msg["role"])
        chat_messages.append(ChatMessage(role=role, content=msg["content"]))

    # Create task record before dispatch
    task_title = messages[-1]["content"][:100] if messages else "Agent task"
    task_id = await tracker.create_task(
        agent_code=agent_code,
        title=task_title,
        client_id=client_id,
        requested_by="NOVA"
    )

    try:
        result = await dispatcher.dispatch(
            agent_code=agent_code,
            messages=chat_messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens
        )

        # Mark task as completed
        await tracker.complete_task(
            task_id=task_id,
            tokens_used=result["tokens_used"],
            provider=result["provider"],
            model=result["model"]
        )

        logger.info(
            f"Agent routing: {agent_code} responded "
            f"({result['provider']}/{result['model']}, "
            f"{result['tokens_used']} tokens)"
        )

        # Format response
        response_content = result["response"]
        if result.get("fallback_used"):
            response_content = (
                f"_[Agent {result['original_agent']} no disponible, "
                f"respondió {result['agent']}]_\n\n{response_content}"
            )

        return {
            "role": "assistant",
            "content": response_content,
            "metadata": {
                "agent": result["agent"],
                "provider": result["provider"],
                "model": result["model"],
                "tokens_used": result["tokens_used"],
                "fallback_used": result.get("fallback_used", False)
            }
        }

    except Exception as e:
        logger.error(f"Agent routing failed for {agent_code}: {e}", exc_info=True)
        raise
