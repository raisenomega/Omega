"""
Queue Manager Service
Pure scheduling and queue management logic
"""
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid


class ScheduledPost(BaseModel):
    """Scheduled social media post"""
    post_id: str
    client_id: str
    platform: str
    content_type: str  # "image" | "video" | "carousel" | "story" | "reel"
    caption: str
    hashtags: List[str]
    media_urls: List[str]
    scheduled_time: str  # ISO datetime
    timezone: str  # "America/New_York" | "America/Puerto_Rico" etc.
    status: str  # "draft" | "pending_approval" | "approved" | "scheduled" | "published" | "failed"
    priority: str  # "low" | "normal" | "high" | "urgent"
    created_by: str  # "ai_generated" | "human_created"
    approved_by: str | None
    approved_at: str | None
    notes: str | None


class PublicationQueue(BaseModel):
    """Publication queue for a client"""
    client_id: str
    total_posts: int
    pending_approval: int
    scheduled_count: int
    published_today: int
    posts: List[ScheduledPost]
    next_publication: ScheduledPost | None


class OptimalTimingResult(BaseModel):
    """Optimal posting time recommendation"""
    platform: str
    recommended_slots: List[str]  # List of ISO datetimes
    reasoning: str
    expected_engagement_boost: float  # Multiplier vs posting at wrong time
    audience_timezone: str


def generate_post_id() -> str:
    """
    Generate unique post ID

    Returns:
        Unique post identifier
    """
    return f"post_{uuid.uuid4().hex[:12]}"


def validate_scheduled_time(scheduled_time: str, platform: str) -> bool:
    """
    Validate if scheduled time is acceptable for platform

    Args:
        scheduled_time: ISO datetime string
        platform: Target platform

    Returns:
        True if timing is valid
    """
    try:
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        now = datetime.now(scheduled_dt.tzinfo)

        # Must be in the future
        if scheduled_dt <= now:
            return False

        # Platform-specific rules
        hour = scheduled_dt.hour

        # Avoid dead zones (2am-5am in any timezone)
        if 2 <= hour < 5:
            return False

        return True

    except (ValueError, AttributeError):
        return False


def sort_queue_by_priority(posts: List[ScheduledPost]) -> List[ScheduledPost]:
    """
    Sort queue by priority and scheduled time

    Args:
        posts: List of scheduled posts

    Returns:
        Sorted list (urgent first, then by time)
    """
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}

    return sorted(
        posts,
        key=lambda p: (
            priority_order.get(p.priority, 2),
            p.scheduled_time
        )
    )


def calculate_optimal_frequency(platform: str, account_size: str) -> dict[str, int]:
    """
    Calculate optimal posting frequency for platform

    Args:
        platform: Social media platform
        account_size: "small" | "medium" | "large"

    Returns:
        Dictionary with daily and weekly targets
    """
    # Base frequencies (posts per week)
    base_frequencies = {
        "instagram": {"small": 7, "medium": 10, "large": 14},
        "tiktok": {"small": 14, "medium": 21, "large": 28},
        "facebook": {"small": 5, "medium": 7, "large": 10},
        "twitter": {"small": 14, "medium": 21, "large": 35},
        "linkedin": {"small": 3, "medium": 5, "large": 7}
    }

    weekly = base_frequencies.get(platform, {"small": 7, "medium": 10, "large": 14})[account_size]
    daily = round(weekly / 7, 1)

    return {
        "posts_per_day": daily,
        "posts_per_week": weekly,
        "platform": platform,
        "account_size": account_size
    }


def filter_posts_by_status(
    posts: List[ScheduledPost],
    status_filter: str | None
) -> List[ScheduledPost]:
    """
    Filter posts by status

    Args:
        posts: List of posts
        status_filter: Status to filter by (or None for all)

    Returns:
        Filtered list
    """
    if not status_filter:
        return posts

    return [p for p in posts if p.status == status_filter]


def filter_posts_by_platform(
    posts: List[ScheduledPost],
    platform_filter: str | None
) -> List[ScheduledPost]:
    """
    Filter posts by platform

    Args:
        posts: List of posts
        platform_filter: Platform to filter by (or None for all)

    Returns:
        Filtered list
    """
    if not platform_filter:
        return posts

    return [p for p in posts if p.platform == platform_filter]


def get_next_publication(posts: List[ScheduledPost]) -> ScheduledPost | None:
    """
    Get next scheduled publication

    Args:
        posts: List of scheduled posts

    Returns:
        Next post to be published (or None)
    """
    approved_posts = [p for p in posts if p.status in ["approved", "scheduled"]]

    if not approved_posts:
        return None

    return min(approved_posts, key=lambda p: p.scheduled_time)
