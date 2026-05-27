"""Use case: Stripe Checkout session para activar ARIA Premium addon.

DEBT-037 V1 · client_aria_premium ($12/mes · sube aria_level +1 max 4).
(DEBT-046 · reseller path → reseller_aria.py.)

Storage: entry se persiste en client_plans.addons (client) o resellers.addons
(reseller) jsonb tras webhook checkout.session.completed → _addon_handlers.
Frontend redirect a checkout_url devuelto.
"""
import logging
from app.bc_billing.domain.plan_pricing import get_price_id_for_addon
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_VALID_ADDONS_CLIENT = ("aria_premium_client",)


def has_active_aria_premium(addons: list[dict]) -> bool:
    """True si addons jsonb tiene aria_premium activo (deactivated_at NULL)."""
    return any(
        a.get("addon_code", "").startswith("aria_premium")
        and a.get("deactivated_at") is None
        for a in (addons or [])
    )


async def create_aria_premium_checkout(
    client_id: str, addon_code: str, success_url: str, cancel_url: str,
) -> BillingResult:
    """Crea Stripe Checkout para activar ARIA Premium addon (client path)."""
    if addon_code not in _VALID_ADDONS_CLIENT:
        return fail(f"addon_code inválido para client: {addon_code}", "invalid_addon_code")

    price_id = get_price_id_for_addon(addon_code)
    if price_id is None:
        return fail(f"Stripe Price ID no configurado para {addon_code}", "price_not_configured")

    supabase = get_supabase_service()
    client_row = supabase.client.table("clients").select(
        "id, name, stripe_customer_id"
    ).eq("id", client_id).execute()
    if not client_row.data:
        return fail(f"Cliente {client_id} no encontrado", "client_not_found")
    client = client_row.data[0]

    plan_row = supabase.client.table("client_plans").select("addons").eq("client_id", client_id).execute()
    addons = (plan_row.data[0].get("addons") if plan_row.data else None) or []
    if has_active_aria_premium(addons):
        return fail("ARIA Premium ya activo para este cliente", "already_active")

    adapter = get_stripe_adapter()
    stripe_customer_id = client.get("stripe_customer_id")
    if not stripe_customer_id:
        customer = adapter.create_customer(
            metadata={"client_id": client_id, "client_name": client.get("name") or ""}
        )
        stripe_customer_id = customer.id
        supabase.client.table("clients").update(
            {"stripe_customer_id": stripe_customer_id}
        ).eq("id", client_id).execute()

    session = adapter.create_checkout_session(
        customer_id=stripe_customer_id, price_id=price_id,
        success_url=success_url, cancel_url=cancel_url,
        metadata={"client_id": client_id, "addon_code": addon_code},
    )
    logger.info(f"ARIA Premium checkout · cliente {client_id} · addon {addon_code} · session {session.id}")
    return ok({"checkout_url": session.url, "session_id": session.id})
