"""
Image generation function for Content Creator Agent
Handles Nano Banana image generation (Fase 2 §2.4 swap from DALL-E 3)
"""
from typing import Dict, Any
import logging
from app.bc_cognition.infrastructure._image_compat import generate_image_compat

logger = logging.getLogger(__name__)


async def generate_image(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate image with Nano Banana

    Args:
        task: Task parameters including optional client brief

    Returns:
        Image URLs with metadata (currently data URIs · DEBT-018)
    """
    prompt = task.get("prompt", "")
    size = task.get("size", "1024x1024")
    quality = task.get("quality", "standard")
    brief = task.get("brief")

    # Context injection for image prompt enhancement
    if brief:
        prompt = f"{prompt}\n\nContext for style/branding: {brief}"

    urls = await generate_image_compat(
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
