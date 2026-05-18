"""
Fal Video Agent - Video generation via Fal.ai (Kling, Hunyuan, Wan)
Filosofía: No velocity, only precision 🐢💎
"""
import os
import logging
import asyncio
from typing import Optional
import fal_client

logger = logging.getLogger(__name__)


class FalVideoAgent:
    """Agent for AI video generation using Fal.ai models"""

    MODEL_MAP = {
        "kling": "fal-ai/kling-video/v1.6/standard/text-to-video",
        "hunyuan": "fal-ai/hunyuan-video",
        "wan": "fal-ai/fast-animatediff/t2v"
    }

    # Duration (seconds) → Frames mapping for Wan/Hunyuan
    FRAME_MAP = {
        5: 85,   # 5 seconds = 85 frames (Hunyuan only allows 85 or 129)
        10: 129  # 10 seconds = 129 frames
    }

    def __init__(self):
        # Set FAL_KEY as environment variable for fal_client
        os.environ["FAL_KEY"] = os.getenv("FAL_KEY", "")
        self.default_model = "kling"

    async def execute(
        self,
        prompt: str,
        model: str = "kling",
        duration: int = 5,
        aspect_ratio: str = "16:9"
    ) -> dict:
        """
        Generate video using Fal.ai models

        Args:
            prompt: Text description of the video
            model: Model key (kling, hunyuan, wan)
            duration: Video duration in seconds
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)

        Returns:
            dict with video_url, model, prompt, duration, status
        """
        try:
            # Resolve model name
            model_id = self.MODEL_MAP.get(model, self.MODEL_MAP[self.default_model])

            logger.info(f"FalVideoAgent: Generating video with {model_id}")

            # Prepare arguments based on model
            arguments = {
                "prompt": prompt
            }

            # Model-specific parameters
            if model == "kling":
                # Kling accepts duration as string (5 or 10)
                arguments["duration"] = str(duration)
                arguments["aspect_ratio"] = aspect_ratio
            elif model == "hunyuan":
                # Hunyuan: num_frames (85 or 129), num_inference_steps (max 30)
                arguments["num_frames"] = self.FRAME_MAP.get(duration, 85)
                arguments["num_inference_steps"] = 25
                arguments["resolution"] = "720p"
            elif model == "wan":
                # Wan (fast-animatediff fallback)
                arguments["num_frames"] = 16
                arguments["fps"] = 8
                arguments["guidance_scale"] = 7.5

            # Subscribe to Fal model (async with timeout for Hunyuan)
            if model == "hunyuan":
                try:
                    result = await asyncio.wait_for(
                        fal_client.subscribe_async(model_id, arguments=arguments),
                        timeout=180.0  # 3 min max for Hunyuan
                    )
                except asyncio.TimeoutError:
                    logger.error(f"FalVideoAgent: Hunyuan timeout after 180s")
                    return {
                        "error": "Hunyuan timeout after 180s",
                        "status": "timeout",
                        "model": model,
                        "prompt": prompt
                    }
            else:
                result = await fal_client.subscribe_async(
                    model_id,
                    arguments=arguments
                )

            # Extract video URL from result
            video_url = None
            if "video" in result and "url" in result["video"]:
                video_url = result["video"]["url"]
            elif "video_url" in result:
                video_url = result["video_url"]
            elif "output" in result:
                video_url = result["output"]

            if not video_url:
                raise Exception(f"No video URL in result: {result.keys()}")

            logger.info(f"FalVideoAgent: Video generated successfully: {video_url}")

            return {
                "video_url": video_url,
                "model": model,
                "model_id": model_id,
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"FalVideoAgent failed: {e}")
            return {
                "error": str(e),
                "status": "failed",
                "model": model,
                "prompt": prompt
            }

    def get_available_models(self) -> dict:
        """Get list of available models"""
        return {
            "kling": {
                "name": "Kling Video V2",
                "description": "High-quality text-to-video from Kuaishou",
                "max_duration": 10,
                "aspect_ratios": ["16:9", "9:16", "1:1"]
            },
            "hunyuan": {
                "name": "Hunyuan Video",
                "description": "Tencent's video generation model",
                "max_duration": 10,
                "aspect_ratios": ["16:9", "9:16", "1:1"]
            },
            "wan": {
                "name": "Wan T2V",
                "description": "Fast text-to-video generation",
                "max_frames": 80,
                "aspect_ratios": ["16:9"]
            }
        }
