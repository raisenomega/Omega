"""
Agent Routing Helper - Detects agent mentions and routes to dispatcher.
DDD: Application layer helper. Max 200L strict.
"""
from typing import Optional, List, Dict, Any
import re
import logging
from app.infrastructure.ai.agent_dispatcher import AgentDispatcher
from app.infrastructure.ai.providers import ChatMessage, MessageRole
from app.infrastructure.calendar import CalendarParser, CalendarRepository
from app.infrastructure.task_tracker import TaskTracker

logger = logging.getLogger(__name__)

# Milagrosa client ID (default for DUDA calendar auto-save)
MILAGROSA_CLIENT_ID = "bd68ca50-b8ef-4240-a0ce-44df58f53171"

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


def _is_calendar_response(response_text: str) -> bool:
    """Detect if response contains calendar patterns."""
    keywords = ["semana", "martes", "miércoles", "jueves", "viernes", "AM", "PM", "post"]
    text_lower = response_text.lower()
    return any(kw in text_lower for kw in keywords)


async def _save_duda_calendar(response_text: str, client_id: str = MILAGROSA_CLIENT_ID) -> Dict[str, Any]:
    """Parse and save DUDA's calendar to Supabase."""
    try:
        posts = CalendarParser().parse(response_text, client_id)
        if not posts:
            return {"inserted": 0, "failed": 0, "ids": []}

        result = await CalendarRepository().save_scheduled_posts(posts, client_id)
        logger.info(f"DUDA auto-save: {result['inserted']} saved, {result['failed']} failed")
        return result
    except Exception as e:
        logger.error(f"Failed to save DUDA calendar: {e}", exc_info=True)
        return {"inserted": 0, "failed": 0, "ids": []}


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

        # DUDA AUTO-SAVE: If DUDA generated a calendar, save it automatically
        if agent_code == "DUDA" and _is_calendar_response(response_content):
            logger.info("Detected DUDA calendar response, auto-saving...")

            # Extract client_id from system_prompt if available
            client_id = MILAGROSA_CLIENT_ID
            if "client" in system_prompt.lower():
                # Try to extract UUID from system prompt
                uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
                match = re.search(uuid_pattern, system_prompt, re.IGNORECASE)
                if match:
                    client_id = match.group(0)
                    logger.info(f"Extracted client_id from system_prompt: {client_id}")

            # Save calendar
            save_result = await _save_duda_calendar(response_content, client_id)

            # Append success message to response
            if save_result["inserted"] > 0:
                response_content += (
                    f"\n\n✅ **{save_result['inserted']} posts guardados "
                    f"automáticamente en el calendario.**"
                )
                if save_result["failed"] > 0:
                    response_content += (
                        f"\n⚠️ {save_result['failed']} posts no pudieron guardarse."
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
