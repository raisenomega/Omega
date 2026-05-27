"""Use case: Stripe Billing Customer Portal session (DEBT-038).

El cliente gestiona su suscripción (método de pago, cancelar, ver facturas)
vía el portal hosteado de Stripe. Flujo: resolvemos el stripe_customer_id del
cliente en la tabla `clients` → creamos una billing_portal.Session → devolvemos
session.url para que el frontend redirija.

503 honesto si Stripe no está configurado (get_stripe_adapter() lanza al init).
409 honesto si el cliente aún no tiene stripe_customer_id (nunca pasó por
checkout · no hay nada que gestionar todavía).
"""
import logging
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def create_customer_portal(client_id: str, return_url: str) -> BillingResult:
    """Crea una Stripe Billing Portal session para el cliente."""
    supabase = get_supabase_service()
    client_row = supabase.client.table("clients").select(
        "id, stripe_customer_id"
    ).eq("id", client_id).execute()
    if not client_row.data:
        return fail(f"Cliente {client_id} no encontrado", "client_not_found")

    stripe_customer_id = client_row.data[0].get("stripe_customer_id")
    if not stripe_customer_id:
        return fail(
            "El cliente aún no tiene suscripción activa para gestionar",
            "no_stripe_customer",
        )

    try:
        adapter = get_stripe_adapter()
    except RuntimeError as e:
        logger.warning(f"customer_portal · Stripe no configurado · {e}")
        return fail(str(e), "stripe_not_configured")

    session = adapter.create_billing_portal_session(
        customer_id=stripe_customer_id, return_url=return_url,
    )
    logger.info(f"Customer Portal · cliente {client_id} · session {session.id}")
    return ok({"portal_url": session.url})
