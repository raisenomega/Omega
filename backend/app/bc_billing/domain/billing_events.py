"""Billing event types + Result<T,E> pattern. Capa pura · cero imports externos.

BillingEventType: enum de eventos Stripe que manejamos.
BillingResult: tuple-like {success, error, error_code, data} análogo a
Result<T,E> de bc_cognition. Use cases retornan este shape.
"""
from enum import Enum
from typing import Optional, Any, TypedDict


class BillingEventType(str, Enum):
    """Eventos Stripe que dispatchamos en process_webhook.

    Otros eventos (invoice.*, payment_method.*, etc.) llegan al webhook
    pero se loguean sin handler dedicado · idempotent register en
    webhook_events para auditoría.
    """
    CHECKOUT_COMPLETED = "checkout.session.completed"
    SUBSCRIPTION_CREATED = "customer.subscription.created"
    SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    INVOICE_PAID = "invoice.paid"


class BillingResult(TypedDict, total=False):
    """Result<T,E> pattern para use cases de billing.

    success=True  + data = ok branch
    success=False + error + error_code = fail branch
    """
    success: bool
    error: Optional[str]
    error_code: Optional[str]
    data: Optional[dict[str, Any]]


def ok(data: Optional[dict[str, Any]] = None) -> BillingResult:
    """Constructor de Result en branch success."""
    return {"success": True, "data": data or {}}


def fail(error: str, error_code: str = "billing_error") -> BillingResult:
    """Constructor de Result en branch fail."""
    return {"success": False, "error": error, "error_code": error_code}
