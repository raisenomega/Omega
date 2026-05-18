"""
Calendar Domain Configuration
Business rules and plan limits
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict
from .types import UserPlan


# Plan limits: posts per day
PLAN_LIMITS: Dict[UserPlan, float] = {
    "basico_97": 2,          # Basic: 2 posts/day
    "pro_197": 5,            # Pro: 5 posts/day
    "enterprise_497": float("inf"),  # Enterprise: unlimited
}


def get_daily_limit(plan: str) -> float:
    """
    Get daily post limit for a plan

    Args:
        plan: User plan identifier

    Returns:
        Daily post limit (float('inf') for unlimited)

    Raises:
        ValueError: If plan is invalid
    """
    # Normalize plan string
    plan_normalized = plan.lower() if plan else "basico_97"

    # Handle legacy plan names
    if plan_normalized == "basic":
        plan_normalized = "basico_97"
    elif plan_normalized == "pro":
        plan_normalized = "pro_197"
    elif plan_normalized == "enterprise":
        plan_normalized = "enterprise_497"

    # Get limit
    if plan_normalized not in PLAN_LIMITS:
        # Default to basic if unknown
        return PLAN_LIMITS["basico_97"]

    return PLAN_LIMITS[plan_normalized]


def can_schedule_more(
    current_count: int,
    plan: str
) -> bool:
    """
    Check if user can schedule more posts for the day

    Args:
        current_count: Number of posts already scheduled for the day
        plan: User plan identifier

    Returns:
        True if user can schedule more posts
    """
    limit = get_daily_limit(plan)
    return current_count < limit


def get_remaining_posts(
    current_count: int,
    plan: str
) -> float:
    """
    Get remaining posts that can be scheduled today

    Args:
        current_count: Number of posts already scheduled
        plan: User plan identifier

    Returns:
        Number of remaining posts (float('inf') for unlimited)
    """
    limit = get_daily_limit(plan)
    if limit == float("inf"):
        return float("inf")
    return max(0, limit - current_count)
