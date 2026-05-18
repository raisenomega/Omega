"""
Handler: Revenue Breakdown from Stripe
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
import os
import stripe

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


async def handle_get_revenue() -> Dict[str, Any]:
    """
    Get revenue breakdown from Stripe

    Returns:
        Dict with MRR, ARR, total revenue, subscriptions breakdown

    Raises:
        HTTPException 500: Stripe error
    """
    try:
        # 1. Active subscriptions breakdown
        subscriptions = stripe.Subscription.list(status='active', limit=100)

        mrr = 0
        subscriptions_by_plan = {}

        for sub in subscriptions.data:
            if sub.plan.interval == 'month':
                amount = sub.plan.amount / 100
                mrr += amount

                plan_name = sub.plan.nickname or sub.plan.id
                if plan_name not in subscriptions_by_plan:
                    subscriptions_by_plan[plan_name] = {"count": 0, "revenue": 0}

                subscriptions_by_plan[plan_name]["count"] += 1
                subscriptions_by_plan[plan_name]["revenue"] += amount

        # 2. Total revenue from charges
        charges = stripe.Charge.list(limit=100)
        total_revenue = sum(c.amount / 100 for c in charges.data if c.paid)

        # Recent charges
        recent_charges = [
            {
                "id": c.id,
                "amount": c.amount / 100,
                "currency": c.currency,
                "paid": c.paid,
                "created": c.created
            }
            for c in charges.data[:10]
        ]

        # 3. Customer stats
        customers = stripe.Customer.list(limit=100)
        total_customers = len(customers.data)

        logger.info(f"Revenue data: MRR=${mrr:.2f}, Total=${total_revenue:.2f}")

        return {
            "mrr": round(mrr, 2),
            "arr": round(mrr * 12, 2),
            "total_revenue": round(total_revenue, 2),
            "total_customers": total_customers,
            "active_subscriptions": len(subscriptions.data),
            "subscriptions_by_plan": subscriptions_by_plan,
            "recent_charges": recent_charges
        }

    except Exception as e:
        logger.error(f"Error getting revenue data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue: {str(e)}")
