"""Stripe-specific types · re-exports de Result para conveniencia.

Mantiene la convención bc_cognition/infrastructure/_anthropic_types.py:
helpers de tipado encapsulados por bounded context.
"""
from typing import TypedDict
from app.bc_billing.domain.billing_events import BillingResult, ok, fail


class StripeEventDict(TypedDict, total=False):
    """Shape simplificada de un Stripe event payload.

    Acceso real al event va vía stripe.Event (dict-like) retornado por
    Webhook.construct_event. Esta TypedDict es para anotación interna.
    """
    id: str
    type: str
    data: dict
    created: int
    livemode: bool


__all__ = ["BillingResult", "ok", "fail", "StripeEventDict"]
