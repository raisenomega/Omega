"""Use case: Stripe Checkout para activar un Agent Add-On (DEBT-091).

5 agentes vendibles (recurring monthly · /add-ons): Publicador/Creativo/Tendencias.
Requiere plan pago (adopcion rechazado). Permite varios agentes simultáneos, pero
NO el mismo code dos veces (ya activo → already_active). 503 honesto si price vacío.
Storage: client_plans.addons jsonb (addon_code=agent_<code>) tras webhook →
_agent_addon_handlers.handle_agent_addon_activation. Mismo patrón que video packs.
"""
import logging
from app.bc_billing.domain.agent_addon_pricing import (
    AGENT_ADDON_CODES, get_price_id_for_agent_addon,
)
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_PAID_PLANS = ("basic", "pro", "enterprise")


def has_active_agent_addon(addons: list[dict], code: str) -> bool:
    """True si client_plans.addons ya tiene este agent add-on activo (deactivated_at NULL)."""
    target = f"agent_{code}"
    return any(
        a.get("addon_code") == target and a.get("deactivated_at") is None
        for a in (addons or [])
    )


async def create_agent_addon_checkout(
    client_id: str, agent_addon_code: str, success_url: str, cancel_url: str,
) -> BillingResult:
    """Crea Stripe Checkout para activar un Agent Add-On."""
    if agent_addon_code not in AGENT_ADDON_CODES:
        return fail(f"agent_addon_code inválido: {agent_addon_code}", "invalid_agent_addon_code")

    price_id = get_price_id_for_agent_addon(agent_addon_code)
    if price_id is None:
        return fail(f"Stripe Price ID no configurado para agent_{agent_addon_code}", "price_not_configured")

    supabase = get_supabase_service()
    client_row = supabase.client.table("clients").select(
        "id, name, plan, stripe_customer_id"
    ).eq("id", client_id).execute()
    if not client_row.data:
        return fail(f"Cliente {client_id} no encontrado", "client_not_found")
    client = client_row.data[0]

    if (client.get("plan") or "adopcion") not in _PAID_PLANS:
        return fail("Los Agentes requieren un plan pago (basic/pro/enterprise)", "requires_paid_plan")

    plan_row = supabase.client.table("client_plans").select("addons").eq("client_id", client_id).execute()
    if not plan_row.data:
        return fail(f"client_plans row no existe para {client_id}", "client_plans_missing")
    addons = plan_row.data[0].get("addons") or []
    if has_active_agent_addon(addons, agent_addon_code):
        return fail("Ya tenés este agente activo", "already_active")

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
        metadata={"client_id": client_id, "agent_addon_code": agent_addon_code},
    )
    logger.info(f"Agent Add-On checkout · cliente {client_id} · agente {agent_addon_code} · session {session.id}")
    return ok({"checkout_url": session.url, "session_id": session.id})
