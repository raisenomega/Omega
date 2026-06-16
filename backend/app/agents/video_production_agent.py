"""
Video Production Agent
Specialized in video script writing and production planning
"""
from typing import Dict, Any
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.services.video_pipeline import VideoSpec, VideoScript
from ._video_production_script_mixin import VideoProductionScriptMixin
from ._video_production_content_mixin import VideoProductionContentMixin
from app.bc_cognition.domain.routing_table import MODEL_SONNET

logger = logging.getLogger(__name__)


class VideoProductionAgent(VideoProductionScriptMixin, VideoProductionContentMixin, BaseAgent):
    """
    Agent specialized in video production
    - Video script writing with powerful hooks
    - Production planning with shot lists
    - Hook optimization for first 3 seconds
    - Platform adaptation
    - Video idea generation
    """

    def __init__(self, agent_id: str = "video_production_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CONTENT_CREATOR,
            model=MODEL_SONNET,
            tools=["script_writer", "hook_optimizer", "shot_planner", "platform_adapter"],
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute video production task"""
        self.set_state(AgentState.WORKING)
        try:
            task_type = task.get("type")
            if task_type == "write_script":
                result = await self.write_video_script(
                    VideoSpec(**task["spec"]), task["brand_voice"], task["key_message"]
                )
            elif task_type == "production_plan":
                result = await self.create_production_plan(
                    VideoSpec(**task["spec"]), VideoScript(**task["script"])
                )
            elif task_type == "optimize_hook":
                result = await self.optimize_hook(
                    task["platform"], task["niche"], task["content_topic"]
                )
            elif task_type == "adapt_script":
                result = await self.adapt_script_for_platform(
                    VideoScript(**task["script"]), task["target_platform"]
                )
            elif task_type == "generate_ideas":
                result = await self.generate_video_ideas(
                    task["niche"], task["platform"], task["content_pillars"]
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"Video production execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise


# Global instance
video_production_agent = VideoProductionAgent()
