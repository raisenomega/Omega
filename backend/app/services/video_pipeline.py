"""
Video Pipeline Service
Pure video production models and validation logic
"""
from pydantic import BaseModel
from typing import List
import uuid


class VideoScene(BaseModel):
    """Individual video scene"""
    scene_number: int
    duration_seconds: int
    narration: str
    visual_description: str
    text_overlay: str | None
    transition: str  # "cut" | "fade" | "slide"


class VideoScript(BaseModel):
    """Complete video script"""
    hook: str  # First 3 seconds - critical for retention
    scenes: List[VideoScene]
    call_to_action: str
    total_duration_seconds: int
    word_count: int


class VideoSpec(BaseModel):
    """Video specifications"""
    title: str
    duration_seconds: int  # 15 | 30 | 60 | 90 | 120
    platform: str  # "tiktok" | "instagram_reels" | "youtube_shorts" | "facebook_reels"
    aspect_ratio: str  # "9:16" | "1:1" | "16:9"
    style: str  # "educational" | "entertainment" | "promotional" | "behind_scenes" | "tutorial"
    visual_style: str  # "minimal" | "dynamic" | "luxury" | "raw" | "corporate"
    target_audience: str


class VideoProductionPlan(BaseModel):
    """Complete production plan"""
    spec: VideoSpec
    script: VideoScript
    shot_list: List[str]
    text_overlays: List[dict[str, str]]
    audio_suggestions: List[str]
    estimated_production_hours: float
    production_tips: List[str]


def calculate_scene_count(total_seconds: int, avg_scene_duration: int = 5) -> int:
    """
    Calculate optimal scene count for video duration

    Args:
        total_seconds: Total video duration
        avg_scene_duration: Average scene duration (default 5s)

    Returns:
        Number of recommended scenes
    """
    if avg_scene_duration <= 0:
        return 1

    scene_count = total_seconds // avg_scene_duration
    return max(1, scene_count)


def validate_duration_for_platform(platform: str, duration: int) -> bool:
    """
    Validate if duration is acceptable for platform

    Args:
        platform: Target platform
        duration: Video duration in seconds

    Returns:
        True if duration is valid for platform
    """
    platform_limits = {
        "tiktok": (5, 180),  # 5s to 3min
        "instagram_reels": (5, 90),  # 5s to 90s
        "youtube_shorts": (5, 60),  # 5s to 60s
        "facebook_reels": (5, 90)  # 5s to 90s
    }

    if platform not in platform_limits:
        return True  # Unknown platform, allow any duration

    min_duration, max_duration = platform_limits[platform]
    return min_duration <= duration <= max_duration


def get_optimal_aspect_ratio(platform: str) -> str:
    """
    Get optimal aspect ratio for platform

    Args:
        platform: Target platform

    Returns:
        Optimal aspect ratio string
    """
    platform_ratios = {
        "tiktok": "9:16",
        "instagram_reels": "9:16",
        "youtube_shorts": "9:16",
        "facebook_reels": "9:16",
        "instagram_feed": "1:1",
        "linkedin": "16:9"
    }

    return platform_ratios.get(platform, "9:16")


def estimate_word_count(duration_seconds: int) -> int:
    """
    Estimate word count for video narration
    Average speaking pace: 150 words per minute

    Args:
        duration_seconds: Video duration in seconds

    Returns:
        Estimated word count
    """
    words_per_second = 150 / 60  # 2.5 words per second
    return int(duration_seconds * words_per_second)


def generate_video_id() -> str:
    """Generate unique video ID"""
    return f"video_{uuid.uuid4().hex[:12]}"
