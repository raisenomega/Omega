"""
Runway Agent - Video generation with Runway Gen-3 Alpha Turbo
Filosofía: No velocity, only precision 🐢💎
"""
import os
import logging
import asyncio
from typing import Optional
from runwayml import RunwayML

logger = logging.getLogger(__name__)


class RunwayAgent:
    """Agent for AI video generation using Runway Gen-3 Alpha Turbo"""

    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY", "")
        self.client = RunwayML(api_key=self.api_key) if self.api_key else None
        self.model = "gen3a_turbo"

    async def execute(
        self,
        prompt: str,
        duration: int = 5,
        ratio: str = "1280:768",
        prompt_image: Optional[str] = None
    ) -> dict:
        """
        Generate video using Runway Gen-3 Alpha Turbo

        Args:
            prompt: Text description of the video
            duration: Video duration in seconds (5 or 10)
            ratio: Video aspect ratio (default: 1280:768)
            prompt_image: Optional image URL for image-to-video

        Returns:
            dict with video_url, duration, model, prompt
        """
        try:
            # Validate API key format
            if not self.api_key or not self.api_key.startswith("key_"):
                logger.error("RunwayAgent: Invalid API key format")
                return {
                    "error": "RUNWAY_API_KEY must start with 'key_'. Update in Railway Dashboard.",
                    "status": "config_error",
                    "prompt": prompt,
                    "model": self.model
                }

            logger.info(f"RunwayAgent: Generating video with prompt: {prompt[:50]}...")

            # Create video generation task
            task = self.client.image_to_video.create(
                model=self.model,
                prompt_text=prompt,
                prompt_image=prompt_image,
                duration=duration,
                ratio=ratio
            )

            logger.info(f"RunwayAgent: Task created with ID: {task.id}")

            # Poll for completion (max 120 seconds)
            max_attempts = 40  # 40 * 3s = 120s
            attempt = 0

            while attempt < max_attempts:
                await asyncio.sleep(3)  # Check every 3 seconds

                # Get task status
                task = self.client.tasks.retrieve(task.id)

                logger.info(f"RunwayAgent: Task status: {task.status} (attempt {attempt + 1}/{max_attempts})")

                if task.status == "SUCCEEDED":
                    video_url = task.output[0] if task.output else None

                    if not video_url:
                        raise Exception("Video generation succeeded but no output URL")

                    logger.info(f"RunwayAgent: Video generated successfully: {video_url}")

                    return {
                        "video_url": video_url,
                        "duration": duration,
                        "model": self.model,
                        "prompt": prompt,
                        "task_id": task.id,
                        "ratio": ratio,
                        "status": "success"
                    }

                elif task.status == "FAILED":
                    error_msg = getattr(task, 'failure', {}).get('reason', 'Unknown error')
                    logger.error(f"RunwayAgent: Task failed: {error_msg}")
                    raise Exception(f"Video generation failed: {error_msg}")

                elif task.status in ("PENDING", "RUNNING"):
                    attempt += 1
                    continue

                else:
                    logger.warning(f"RunwayAgent: Unknown status: {task.status}")
                    attempt += 1

            # Timeout
            raise Exception(f"Video generation timed out after {max_attempts * 3} seconds")

        except Exception as e:
            logger.error(f"RunwayAgent failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "prompt": prompt,
                "model": self.model
            }

    async def check_credits(self) -> dict:
        """Check remaining Runway credits"""
        try:
            # Note: Runway SDK may not have credits endpoint
            # Return placeholder for now
            return {
                "credits_available": "unknown",
                "message": "Credits check not implemented in SDK"
            }
        except Exception as e:
            logger.error(f"Credits check failed: {e}")
            return {"error": str(e)}
