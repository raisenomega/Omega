"""
Image generation function for Content Creator Agent
Handles DALL-E 3 image generation
"""
from typing import Dict, Any
import logging
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


async def generate_image(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate image with DALL-E 3

    Args:
        task: Task parameters including optional client brief

    Returns:
        Image URLs with metadata
    """
    prompt = task.get("prompt", "")
    size = task.get("size", "1024x1024")
    quality = task.get("quality", "standard")
    brief = task.get("brief")

    # Context injection for image prompt enhancement
    if brief:
        prompt = f"{prompt}\n\nContext for style/branding: {brief}"

    urls = await openai_service.generate_image(
        prompt=prompt,
        size=size,
        quality=quality
    )

    return {
        "image_urls": urls,
        "prompt": prompt,
        "size": size,
        "quality": quality
    }
