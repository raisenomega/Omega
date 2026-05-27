"""DEBT-052 FASE 4 (5/5) · auto-recarga de credit packs.

Toggle en packs jsonb (set_auto_recharge). Cuando el saldo cae a ≤20% (consumido ≥
RECHARGE_THRESHOLD·budget) y el toggle está ON, maybe_auto_recharge intenta un cobro
off-session en Stripe por el precio del tier; si tiene éxito, recarga el budget
(+pack_budget) + ledger __auto_recharge__.

HONESTO (cero mocks): si Stripe no está configurado (sin secret key / sin payment
method / price del tier vacío) → log + BillingResult fail (503-equivalente), CERO
fabricación de éxito, CERO cambio de budget.
"""
import logging
import asyncio
from typing import Optional
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.domain.credit_costs import pack_budget_usd, RECHARGE_THRESHOLD
from app.bc_billing.domain.credit_pack_pricing import get_price_id_for_credit_pack
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _active_pack(packs) -> Optional[dict]:
    return next((p for p in (packs or []) if p.get("tier") and p.get("deactivated_at") is None), None)


def _set_toggle_sync(client_id: str, enabled: bool) -> BillingResult:
    sb = get_supabase_service().client
    r = sb.table("client_agent_credits").select("packs").eq("client_id", client_id).limit(1).execute()
    if not r.data:
        return fail("Cliente no enrolado (sin credit pack)", "not_enrolled")
    packs = r.data[0].get("packs") or []
    active = _active_pack(packs)
    if active is None:
        return fail("Sin credit pack activo", "no_active_pack")
    active["auto_recharge"] = enabled
    sb.table("client_agent_credits").update({"packs": packs}).eq("client_id", client_id).execute()
    return ok({"auto_recharge": enabled})


async def set_auto_recharge(client_id: str, enabled: bool) -> BillingResult:
    """Activa/desactiva el toggle de auto-recarga del credit pack activo (packs jsonb)."""
    try:
        return await asyncio.to_thread(_set_toggle_sync, client_id, enabled)
    except Exception as e:
        logger.error(f"set_auto_recharge failed · client={client_id}: {e}")
        return fail(f"Error de infraestructura: {e}", "infra_error")


def _recharge_sync(client_id: str) -> BillingResult:
    sb = get_supabase_service().client
    r = (sb.table("client_agent_credits")
         .select("budget_usd_mensual, consumido_usd, packs").eq("client_id", client_id).limit(1).execute())
    if not r.data:
        return fail("no enrolado", "not_enrolled")
    row = r.data[0]
    budget = float(row.get("budget_usd_mensual") or 0)
    if budget <= 0 or float(row.get("consumido_usd") or 0) < RECHARGE_THRESHOLD * budget:
        return fail("aún no alcanza el umbral", "below_threshold")
    active = _active_pack(row.get("packs"))
    if active is None or not active.get("auto_recharge"):
        return fail("auto-recarga desactivada", "disabled")
    tier = active.get("tier")
    price_id = get_price_id_for_credit_pack(tier)
    if price_id is None:
        return fail(f"Stripe Price no configurado para credit_pack_{tier}", "price_not_configured")
    c = sb.table("clients").select("stripe_customer_id").eq("id", client_id).limit(1).execute()
    customer_id = c.data[0].get("stripe_customer_id") if c.data else None
    if not customer_id:
        return fail("Cliente sin stripe_customer_id", "no_stripe_customer")
    from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
    get_stripe_adapter().charge_off_session(customer_id, price_id)  # raises sin PM → honesto
    add = pack_budget_usd(tier)
    sb.table("client_agent_credits").update(
        {"budget_usd_mensual": budget + add}).eq("client_id", client_id).execute()
    sb.table("client_credit_ledger").insert({
        "client_id": client_id, "agent_code": "__auto_recharge__", "cost_usd": add, "model": f"tier:{tier}",
    }).execute()
    return ok({"recharged_usd": add, "budget_usd_mensual": budget + add})


async def maybe_auto_recharge(client_id: str) -> BillingResult:
    """Best-effort tras débito: si saldo ≤20% y toggle ON → cobro off-session + top-up.
    HONESTO: Stripe no configurado/falla → log + fail, CERO cambio de budget."""
    try:
        result = await asyncio.to_thread(_recharge_sync, client_id)
    except Exception as e:
        logger.warning(f"auto_recharge no realizada (honesto · sin fabricar) · client={client_id}: {e}")
        return fail(f"auto-recarga no disponible: {e}", "recharge_unavailable")
    if result.get("success"):
        logger.info(f"auto_recharge OK · client={client_id} · +${result['data']['recharged_usd']}")
    return result
