"""
Billing Checkout Endpoint
Stripe checkout session creation for subscriptions
"""
import os
from fastapi import APIRouter, HTTPException
from app.api.routes.billing.models import (
    CreateCheckoutSessionRequest,
    CheckoutSessionResponse,
)
from app.api.routes.billing.stripe_config import (
    stripe,
    get_price_id,
    TRIAL_PERIOD_DAYS,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Checkout URLs from environment (with defaults)
STRIPE_SUCCESS_URL = os.environ.get(
    "STRIPE_SUCCESS_URL",
    "https://r-omega.agency/dashboard?session_id={CHECKOUT_SESSION_ID}"
)
STRIPE_CANCEL_URL = os.environ.get(
    "STRIPE_CANCEL_URL",
    "https://r-omega.agency/pricing"
)


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest
) -> CheckoutSessionResponse:
    """
    Create Stripe Checkout session for subscription

    Args:
        request: CreateCheckoutSessionRequest with client_id, plan, trial

    Returns:
        CheckoutSessionResponse with checkout_url and session_id

    Raises:
        HTTPException 400: Invalid plan
        HTTPException 402: Stripe API error (payment required)
        HTTPException 500: Server error

    Flow:
        1. Validate plan via get_price_id() (basic|pro|enterprise)
        2. Create checkout session with trial if requested (7 days)
        3. Return checkout URL for client to complete payment
    """
    try:
        # Get price ID for plan (validates and raises ValueError if invalid)
        try:
            price_id = get_price_id(request.plan)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Create checkout session parameters
        checkout_params = {
            "mode": "subscription",
            "line_items": [{
                "price": price_id,
                "quantity": 1
            }],
            "success_url": STRIPE_SUCCESS_URL,
            "cancel_url": STRIPE_CANCEL_URL,
            "metadata": {
                "client_id": request.client_id,
                "plan": request.plan
            }
        }

        # Add trial if requested (uses TRIAL_PERIOD_DAYS from config)
        if request.trial:
            checkout_params["subscription_data"] = {
                "trial_period_days": TRIAL_PERIOD_DAYS
            }

        # Create checkout session via Stripe API
        session = stripe.checkout.Session.create(**checkout_params)

        logger.info(
            f"Checkout session created for client {request.client_id}, "
            f"plan: {request.plan}, trial: {request.trial}"
        )

        return CheckoutSessionResponse(
            success=True,
            checkout_url=session.url,
            session_id=session.id,
            message="Checkout session created successfully"
        )

    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {e}")
        raise HTTPException(status_code=402, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="An error occurred creating checkout session")
