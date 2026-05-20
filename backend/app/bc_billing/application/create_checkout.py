"""Use case: crear Stripe Checkout session para upgrade Adopción→Básico o Básico→Pro.

Opción A confirmada (19 may 2026): Stripe Customer creado ANTES del checkout
si cliente no tiene `stripe_customer_id` todavía · evita duplicados de
Customer en re-intentos abandonados · webhook luego matchea by customer_id.
"""
import logging
from app.bc_billing.domain.plan_pricing import get_price_id_for_plan, is_valid_upgrade
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def create_checkout_for_upgrade(
    client_id: str,
    target_plan: str,
    success_url: str,
    cancel_url: str,
) -> BillingResult:
    """Crea Stripe Checkout session para upgrade.

    Args:
        client_id: UUID del cliente que está haciendo el upgrade
        target_plan: 'basic' o 'pro' (adopcion rechazado · trial gratis)
        success_url: redirect post-payment
        cancel_url: redirect si user cancela

    Returns:
        BillingResult con data={'checkout_url', 'session_id'} o error_code apropiado.
    """
    if target_plan not in ("basic", "pro"):
        return fail(
            f"target_plan debe ser 'basic' o 'pro', got '{target_plan}'",
            "invalid_target_plan",
        )

    price_id = get_price_id_for_plan(target_plan)
    if price_id is None:
        return fail(
            f"Stripe Price ID no configurado para plan '{target_plan}'",
            "price_not_configured",
        )

    supabase = get_supabase_service()
    client_row = (
        supabase.client.table("clients")
        .select("id, name, plan, stripe_customer_id")
        .eq("id", client_id)
        .execute()
    )
    if not client_row.data:
        return fail(f"Cliente {client_id} no encontrado", "client_not_found")

    client = client_row.data[0]
    if not is_valid_upgrade(client["plan"], target_plan):
        return fail(
            f"Upgrade inválido: {client['plan']} → {target_plan}",
            "invalid_upgrade_path",
        )

    adapter = get_stripe_adapter()
    stripe_customer_id = client.get("stripe_customer_id")

    # Opción A: crear Stripe Customer antes del checkout si no existe
    if not stripe_customer_id:
        customer = adapter.create_customer(
            metadata={"client_id": client_id, "client_name": client.get("name") or ""}
        )
        stripe_customer_id = customer.id
        supabase.client.table("clients").update(
            {"stripe_customer_id": stripe_customer_id}
        ).eq("id", client_id).execute()
        logger.info(f"Stripe Customer {stripe_customer_id} creado para cliente {client_id}")

    session = adapter.create_checkout_session(
        customer_id=stripe_customer_id,
        price_id=price_id,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"client_id": client_id, "target_plan": target_plan},
    )
    logger.info(f"Checkout session {session.id} · cliente {client_id} → {target_plan}")

    return ok({"checkout_url": session.url, "session_id": session.id})
