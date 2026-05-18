"""
Content Creator Agent
Main agent class with task routing
"""
from typing import Dict, Any
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.agents.content_creator.text_generation import (
    generate_caption,
    generate_hashtags,
    generate_video_script
)
from app.agents.content_creator.image_generation import generate_image

logger = logging.getLogger(__name__)


class ContentCreatorAgent(BaseAgent):
    """
    Agent specialized in content generation
    - Text captions
    - Hashtags
    - Images
    - Video scripts
    """

    def __init__(self, agent_id: str = "content_creator_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CONTENT_CREATOR,
            model="gpt-4o",
            tools=["text_generation", "image_generation", "hashtag_research"]
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content generation task

        Args:
            task: Task parameters
                - type: "caption" | "image" | "hashtags" | "video_script"
                - topic: Content topic
                - platform: Target platform
                - tone: Content tone
                - brief: Optional client context for personalization

        Returns:
            Generated content
        """
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "caption":
                result = await generate_caption(task)
            elif task_type == "image":
                result = await generate_image(task)
            elif task_type == "hashtags":
                result = await generate_hashtags(task)
            elif task_type == "video_script":
                result = await generate_video_script(task)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            # Store in memory
            await self.store_memory(f"last_{task_type}", result)

            self.set_state(AgentState.IDLE)
            return result

        except Exception as e:
            logger.error(f"Content creation error: {e}")
            self.set_state(AgentState.ERROR)
            raise


# Global instance
content_creator_agent = ContentCreatorAgent()
