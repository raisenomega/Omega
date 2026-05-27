"""Único entry point a Stripe SDK · ÚNICA clase en bc_billing que importa stripe (A4/I1) · init lazy via get_stripe_adapter() · errors al primer uso real."""
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

    def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> stripe.billing_portal.Session:
        """DEBT-038 · portal hosteado para gestionar suscripción (pago/cancelar/facturas)."""
        return stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)

    def verify_and_construct_event(self, payload: bytes, signature: str) -> stripe.Event:
        """Verifica signature webhook + construye event. Lanza si inválido."""
        return stripe.Webhook.construct_event(payload, signature, self._webhook_secret)

    def retrieve_subscription(self, subscription_id: str) -> stripe.Subscription:
        """Recupera subscription para extraer current_period_end real."""
        return stripe.Subscription.retrieve(subscription_id)

    def schedule_downgrade_at_period_end(
        self, subscription_id: str, new_price_id: str
    ) -> stripe.SubscriptionSchedule:
        """DEBT-076 · cambio de precio a fin de ciclo (SubscriptionSchedule · release · webhook sincroniza)."""
        schedule = stripe.SubscriptionSchedule.create(from_subscription=subscription_id)
        phase0 = schedule.phases[0]
        return stripe.SubscriptionSchedule.modify(
            schedule.id,
            end_behavior="release",
            phases=[
                {
                    "items": [{"price": phase0["items"][0]["price"], "quantity": 1}],
                    "start_date": phase0["start_date"],
                    "end_date": phase0["end_date"],
                },
                {"items": [{"price": new_price_id, "quantity": 1}]},
            ],
        )

    def charge_off_session(self, customer_id: str, price_id: str) -> stripe.PaymentIntent:
        """DEBT-052 F4 · cobro inmediato off-session por el monto del price (auto-recarga).
        Lanza si el customer no tiene payment method guardado → el caller lo trata como 503 honesto."""
        price = stripe.Price.retrieve(price_id)
        return stripe.PaymentIntent.create(
            amount=price["unit_amount"], currency=price["currency"], customer=customer_id,
            off_session=True, confirm=True,
            metadata={"reason": "credit_pack_auto_recharge", "price_id": price_id},
        )


_adapter: Optional[StripeAdapter] = None


def get_stripe_adapter() -> StripeAdapter:
    """Lazy singleton · evita init de stripe SDK si bc_billing no se invoca."""
    global _adapter
    if _adapter is None:
        _adapter = StripeAdapter()
    return _adapter
