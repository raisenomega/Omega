"""Único entry point a Stripe SDK. Análogo a `bc_cognition.anthropic_adapter`.

ÚNICA clase/módulo en bc_billing que hace `import stripe`. Cualquier otra
parte del bc_billing accede a Stripe a través de este adapter.

Inicialización lazy via `get_stripe_adapter()` singleton · evita import-time
side effects (no fail-fast bloqueante si .env incompleto · errors se
levantan al primer uso real).
"""
import logging
from typing import Optional
import stripe
from app.config import settings

logger = logging.getLogger(__name__)


class StripeAdapter:
    """Wrapper sobre stripe SDK · única clase que importa stripe en bc_billing."""

    def __init__(self) -> None:
        if not settings.stripe_secret_key:
            raise RuntimeError(
                "STRIPE_SECRET_KEY no configurada · setear en .env antes de usar billing"
            )
        if not settings.stripe_webhook_secret:
            raise RuntimeError(
                "STRIPE_WEBHOOK_SECRET no configurada · setear en .env antes de procesar webhooks"
            )
        stripe.api_key = settings.stripe_secret_key
        self._webhook_secret = settings.stripe_webhook_secret
        logger.info("StripeAdapter initialized (test mode: %s)", settings.stripe_secret_key.startswith("sk_test_"))

    def create_customer(self, metadata: dict) -> stripe.Customer:
        """Crea Stripe Customer con metadata · usado pre-checkout (Opción A)."""
        return stripe.Customer.create(metadata=metadata)

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict] = None,
    ) -> stripe.checkout.Session:
        """Crea Checkout session subscription para customer existente."""
        return stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
        )

    def verify_and_construct_event(self, payload: bytes, signature: str) -> stripe.Event:
        """Verifica signature webhook + construye event. Lanza si inválido."""
        return stripe.Webhook.construct_event(payload, signature, self._webhook_secret)

    def retrieve_subscription(self, subscription_id: str) -> stripe.Subscription:
        """Recupera subscription para extraer current_period_end real."""
        return stripe.Subscription.retrieve(subscription_id)


_adapter: Optional[StripeAdapter] = None


def get_stripe_adapter() -> StripeAdapter:
    """Lazy singleton · evita init de stripe SDK si bc_billing no se invoca."""
    global _adapter
    if _adapter is None:
        _adapter = StripeAdapter()
    return _adapter
