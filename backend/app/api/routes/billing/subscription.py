"""
Billing Subscription Endpoints
Get and cancel subscription for authenticated clients
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.api.routes.billing.stripe_config import stripe
from app.api.routes.billing.models import (
    CancelSubscriptionRequest,
    SubscriptionStatusResponse,
)
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/subscription/{client_id}", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> SubscriptionStatusResponse:
    """
    Get subscription status for authenticated client

    Args:
        client_id: Client UUID (path parameter)
        authorization: Authorization header with JWT token

    Returns:
        SubscriptionStatusResponse with subscription data

    Raises:
        HTTPException 401: Missing or invalid token
        HTTPException 403: Client trying to access another client's subscription
        HTTPException 404: No subscription found
        HTTPException 402: Stripe error
        HTTPException 500: Server error

    Security:
        Verifies that authenticated client_id matches path parameter
        to prevent unauthorized access to other clients' subscriptions
    """
    try:
        # Extract and verify client_id from JWT token
        authenticated_client_id = await get_current_user_id(authorization)

        # Verify client is requesting their own subscription
        if authenticated_client_id != client_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot access another client's subscription"
            )

        # Get subscription from database
        supabase = get_supabase_service()
        subscription_data = await supabase.get_client_subscription(client_id)

        if not subscription_data:
            raise HTTPException(
                status_code=404,
                detail="No subscription found for this client"
            )

        # Check if client has a Stripe subscription
        stripe_subscription_id = subscription_data.get("stripe_subscription_id")
        if not stripe_subscription_id:
            # Return local data if no Stripe subscription
            return SubscriptionStatusResponse(
                success=True,
                data={
                    "client_id": client_id,
                    "subscription_id": None,
                    "status": subscription_data.get("subscription_status", "inactive"),
                    "plan": subscription_data.get("plan"),
                    "trial_active": subscription_data.get("trial_active", False)
                },
                message="Client exists but has no active Stripe subscription"
            )

        # Get live status from Stripe
        subscription = stripe.Subscription.retrieve(stripe_subscription_id)

        return SubscriptionStatusResponse(
            success=True,
            data={
                "client_id": client_id,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "plan": subscription_data.get("plan"),
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "trial_active": subscription_data.get("trial_active", False)
            },
            message="Subscription status retrieved"
        )

    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting subscription: {e}")
        raise HTTPException(status_code=402, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(status_code=500, detail="An error occurred getting subscription status")


@router.post("/cancel-subscription", response_model=SubscriptionStatusResponse)
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    authorization: Optional[str] = Header(None)
) -> SubscriptionStatusResponse:
    """
    Cancel subscription for authenticated client

    Args:
        request: CancelSubscriptionRequest with client_id
        authorization: Authorization header with JWT token

    Returns:
        SubscriptionStatusResponse with cancellation data (cancel_at_period_end)

    Raises:
        HTTPException 401: Missing or invalid token
        HTTPException 403: Client trying to cancel another client's subscription
        HTTPException 404: No subscription found
        HTTPException 402: Stripe error
        HTTPException 500: Server error

    Security:
        Verifies that authenticated client_id matches request.client_id
        to prevent unauthorized cancellation of other clients' subscriptions

    Flow:
        1. Verify authenticated client matches request
        2. Get subscription from database
        3. Cancel in Stripe (cancel_at_period_end=True)
        4. Return cancellation confirmation (DB update happens via webhook)
    """
    try:
        # Extract and verify client_id from JWT token
        authenticated_client_id = await get_current_user_id(authorization)

        # Verify client is cancelling their own subscription
        if authenticated_client_id != request.client_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot cancel another client's subscription"
            )

        # Get subscription from database
        supabase = get_supabase_service()
        subscription_data = await supabase.get_client_subscription(request.client_id)

        if not subscription_data:
            raise HTTPException(
                status_code=404,
                detail="No client found with this ID"
            )

        stripe_subscription_id = subscription_data.get("stripe_subscription_id")
        if not stripe_subscription_id:
            raise HTTPException(
                status_code=404,
                detail="Client has no active Stripe subscription to cancel"
            )

        # Cancel subscription in Stripe (at period end)
        subscription = stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )

        logger.info(
            f"Subscription {stripe_subscription_id} will cancel at period end "
            f"for client {request.client_id}"
        )

        return SubscriptionStatusResponse(
            success=True,
            data={
                "subscription_id": stripe_subscription_id,
                "status": "cancelling",
                "cancel_at": subscription.cancel_at,
                "cancel_at_period_end": subscription.cancel_at_period_end
            },
            message="Subscription will be cancelled at period end"
        )

    except HTTPException:
        raise
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error cancelling subscription: {e}")
        raise HTTPException(status_code=402, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail="An error occurred cancelling subscription")
