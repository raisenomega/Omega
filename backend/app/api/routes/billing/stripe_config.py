"""
Stripe Configuration and Helpers
Fail-fast initialization and price ID management
"""
import os
import stripe
from typing import Final, List
import logging

logger = logging.getLogger(__name__)

# Fail-fast validation for Stripe Secret Key
STRIPE_SECRET_KEY: str = os.environ.get("STRIPE_SECRET_KEY", "")
if not STRIPE_SECRET_KEY:
    raise RuntimeError(
        "STRIPE_SECRET_KEY environment variable is not set. "
        "Configure it in Railway before deploying."
    )

# Load Stripe Price IDs from environment
STRIPE_PRICE_BASIC: str = os.environ.get("STRIPE_PRICE_BASIC", "")
STRIPE_PRICE_PRO: str = os.environ.get("STRIPE_PRICE_PRO", "")
STRIPE_PRICE_ENTERPRISE: str = os.environ.get("STRIPE_PRICE_ENTERPRISE", "")

# Fail-fast validation for all Price IDs
missing_prices = []
if not STRIPE_PRICE_BASIC:
    missing_prices.append("STRIPE_PRICE_BASIC")
if not STRIPE_PRICE_PRO:
    missing_prices.append("STRIPE_PRICE_PRO")
if not STRIPE_PRICE_ENTERPRISE:
    missing_prices.append("STRIPE_PRICE_ENTERPRISE")

if missing_prices:
    raise RuntimeError(
        f"Missing Stripe price IDs: {', '.join(missing_prices)}. "
        "Configure them in Railway before deploying."
    )

# Initialize Stripe SDK
stripe.api_key = STRIPE_SECRET_KEY
logger.info("Stripe SDK initialized successfully")

# Constants
VALID_PLANS: Final[List[str]] = ["basic", "pro", "enterprise"]
TRIAL_PERIOD_DAYS: Final[int] = 7


def get_price_id(plan: str) -> str:
    """
    Get Stripe price ID for subscription plan

    Args:
        plan: Subscription plan (basic|pro|enterprise, case-insensitive)

    Returns:
        Stripe price ID for the plan

    Raises:
        ValueError: If plan is not in VALID_PLANS

    Example:
        >>> get_price_id("basic")
        'price_1ABC123...'
        >>> get_price_id("ENTERPRISE")
        'price_1XYZ789...'
    """
    # Normalize to lowercase
    plan_lower = plan.lower()

    # Validate plan
    if plan_lower not in VALID_PLANS:
        raise ValueError(
            f"Invalid plan: {plan}. Must be one of: {', '.join(VALID_PLANS)}"
        )

    # Map plan to price ID
    plan_prices = {
        "basic": STRIPE_PRICE_BASIC,
        "pro": STRIPE_PRICE_PRO,
        "enterprise": STRIPE_PRICE_ENTERPRISE
    }

    return plan_prices[plan_lower]
