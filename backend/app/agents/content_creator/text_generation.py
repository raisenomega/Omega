"""
Text generation functions for Content Creator Agent
Handles captions, hashtags, and video scripts
"""
from typing import Dict, Any
import logging
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


async def generate_caption(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate social media caption

    Args:
        task: Task parameters including optional client brief

    Returns:
        Caption data with metadata
    """
    topic = task.get("topic", "")
    platform = task.get("platform", "instagram")
    tone = task.get("tone", "professional")
    brief = task.get("brief")

    # Context injection (graceful degradation if no brief)
    context_block = (
        f"\n\nCLIENT CONTEXT — aplica siempre a este contenido:\n{brief}"
        if brief else ""
    )

    system_message = (
        f"You are a social media expert creating content for {platform}. "
        f"Write in a {tone} tone. Keep it engaging and authentic."
        f"{context_block}"
    )

    prompt = (
        f"Create a compelling {platform} caption about: {topic}\n"
        f"Requirements:\n"
        f"- Tone: {tone}\n"
        f"- Include call-to-action\n"
        f"- Optimize for engagement\n"
        f"- Max 2200 characters"
    )

    caption = await openai_service.generate_text(
        prompt=prompt,
        system_message=system_message,
        temperature=0.8
    )

    return {
        "caption": caption,
        "platform": platform,
        "tone": tone,
        "length": len(caption)
    }


async def generate_hashtags(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate relevant hashtags

    Args:
        task: Task parameters including optional client brief

    Returns:
        Hashtag list with metadata
    """
    topic = task.get("topic", "")
    count = task.get("count", 10)
    platform = task.get("platform", "instagram")
    brief = task.get("brief")

    # NOTE: Context injected in user prompt (no system_message in this call)
    context_block = (
        f"\n\nCLIENT CONTEXT — considera para relevancia:\n{brief}"
        if brief else ""
    )

    prompt = (
        f"Generate {count} highly relevant hashtags for {platform} "
        f"about: {topic}\n"
        f"Requirements:\n"
        f"- Mix of popular and niche hashtags\n"
        f"- Relevant to the topic\n"
        f"- Format: #hashtag (one per line)"
        f"{context_block}"
    )

    response = await openai_service.generate_text(
        prompt=prompt,
        temperature=0.6
    )

    # Parse hashtags
    hashtags = [
        line.strip()
        for line in response.split("\n")
        if line.strip().startswith("#")
    ]

    return {
        "hashtags": hashtags[:count],
        "topic": topic,
        "platform": platform
    }


async def generate_video_script(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate video script

    Args:
        task: Task parameters including optional client brief

    Returns:
        Video script with metadata
    """
    topic = task.get("topic", "")
    duration = task.get("duration", 30)
    style = task.get("style", "professional")
    brief = task.get("brief")

    # Context injection (graceful degradation if no brief)
    context_block = (
        f"\n\nCLIENT CONTEXT — aplica al script:\n{brief}"
        if brief else ""
    )

    prompt = (
        f"Create a {duration}-second video script about: {topic}\n"
        f"Style: {style}\n"
        f"Include:\n"
        f"- Hook (first 3 seconds)\n"
        f"- Main content\n"
        f"- Call-to-action\n"
        f"- Visual suggestions"
        f"{context_block}"
    )

    script = await openai_service.generate_text(
        prompt=prompt,
        temperature=0.7,
        max_tokens=500
    )

    return {
        "script": script,
        "duration": duration,
        "style": style,
        "topic": topic
    }
