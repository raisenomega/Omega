"""
Billing Request/Response Models
Pydantic models for Stripe billing endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CreateCheckoutSessionRequest(BaseModel):
    """
    Request to create Stripe checkout session

    Used by: POST /billing/create-checkout-session

    Attributes:
        client_id: Client UUID to associate subscription
        plan: Subscription plan (basic|pro|enterprise)
        trial: Enable 7-day trial period (default: False)
    """
    client_id: str = Field(..., description="Client UUID")
    plan: str = Field(..., description="basic|pro|enterprise")
    trial: bool = Field(default=False, description="Enable 7-day trial period")


class CheckoutSessionResponse(BaseModel):
    """
    Response from Stripe checkout session creation

    Used by: POST /billing/create-checkout-session

    Attributes:
        success: Whether checkout session was created successfully
        checkout_url: Stripe checkout URL for client to complete payment
        session_id: Stripe checkout session ID
        message: Success or error message
        error: Error code (invalid_plan, missing_price_id, stripe_error, server_error)
    """
    success: bool = Field(..., description="Whether operation succeeded")
    checkout_url: Optional[str] = Field(None, description="Stripe checkout URL")
    session_id: Optional[str] = Field(None, description="Stripe session ID")
    message: Optional[str] = Field(None, description="Success or error message")
    error: Optional[str] = Field(None, description="Error code if failed")


class CancelSubscriptionRequest(BaseModel):
    """
    Request to cancel client subscription

    Used by: POST /billing/cancel-subscription

    Attributes:
        client_id: Client UUID whose subscription will be cancelled
    """
    client_id: str = Field(..., description="Client UUID")


class SubscriptionStatusResponse(BaseModel):
    """
    Response with subscription status data

    Used by:
        - POST /billing/cancel-subscription
        - GET /billing/subscription/{client_id}

    Attributes:
        success: Whether operation succeeded
        data: Subscription data (subscription_id, status, plan, trial_active, etc.)
        message: Success or error message
        error: Error code (not_found, no_subscription, stripe_error, server_error)
    """
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Subscription data")
    message: Optional[str] = Field(None, description="Success or error message")
    error: Optional[str] = Field(None, description="Error code if failed")
