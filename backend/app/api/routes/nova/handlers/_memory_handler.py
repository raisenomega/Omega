"""
Memory Handler - Manages agent memory extraction and persistence.
DDD: Application layer helper. Max 200L strict.
"""
from typing import List
import logging
import asyncio

from app.services.agent_memory_service import AgentMemoryService

logger = logging.getLogger(__name__)


def extract_mentioned_agents(messages: List[dict]) -> List[str]:
    """
    Extract mentioned agent codes from recent messages.

    Args:
        messages: List of chat messages (last 3 recommended)

    Returns:
        List of agent codes mentioned
    """
    memory_service = AgentMemoryService()
    recent_text = " ".join([m["content"] for m in messages[-3:]])
    return memory_service.extract_mentioned_agents(recent_text)


async def save_conversation_memory_async(
    user_message: str,
    assistant_message: str,
    messages: List[dict]
) -> None:
    """
    Save conversation memory for mentioned agents asynchronously.

    Args:
        user_message: User's message
        assistant_message: NOVA's response
        messages: Recent message history (last 5 recommended)

    Returns:
        None (saves memory in background)
    """
    memory_service = AgentMemoryService()

    # Extract mentioned agents from full conversation
    all_text = user_message + " " + assistant_message
    mentioned_in_response = memory_service.extract_mentioned_agents(all_text)

    if mentioned_in_response:
        # Create task to save memory without blocking response
        asyncio.create_task(
            memory_service.save_conversation_memory(
                agent_codes=mentioned_in_response,
                user_message=user_message,
                nova_response=assistant_message,
                recent_context=messages[-5:]
            )
        )
        logger.info(f"Saving memory for agents: {', '.join(mentioned_in_response)}")
