"""Use case: Stripe Checkout para comprar un Credit Pack (DEBT-052 FASE 4).

4 packs (budget mensual prepagado de API · texto/imagen): micro $9 / starter $25
/ plus $59 / ultra $119 · recurring monthly (mismo patrón que video packs). El
enrolamiento (fila en client_agent_credits) lo hace el webhook checkout.session.
completed → _credit_pack_handlers.handle_credit_pack_enrollment.

Requiere plan pago (adopcion/trial rechazado · no distorsiona el funnel). Policy
V1: 1 credit pack activo a la vez (re-compra = cancelar el actual primero).
503 honesto si el Stripe Price ID no está configurado.
"""
import logging
from app.bc_billing.domain.credit_pack_pricing import (
    CREDIT_PACK_CODES, get_price_id_for_credit_pack,
)
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_PAID_PLANS = ("basic", "pro", "enterprise")


def has_active_credit_pack(packs: list[dict]) -> bool:
    """True si client_agent_credits.packs tiene un credit pack activo (deactivated_at NULL)."""
    return any(
        p.get("tier") and p.get("deactivated_at") is None
        for p in (packs or [])
    )


async def create_credit_pack_checkout(
    client_id: str, credit_pack_code: str, success_url: str, cancel_url: str,
) -> BillingResult:
    """Crea Stripe Checkout para comprar un Credit Pack."""
    if credit_pack_code not in CREDIT_PACK_CODES:
        return fail(f"credit_pack_code inválido: {credit_pack_code}", "invalid_credit_pack_code")

    price_id = get_price_id_for_credit_pack(credit_pack_code)
    if price_id is None:
        return fail(f"Stripe Price ID no configurado para credit_pack_{credit_pack_code}", "price_not_configured")

    supabase = get_supabase_service()
    client_row = supabase.client.table("clients").select(
        "id, name, plan, stripe_customer_id"
    ).eq("id", client_id).execute()
    if not client_row.data:
        return fail(f"Cliente {client_id} no encontrado", "client_not_found")
    client = client_row.data[0]

    if (client.get("plan") or "adopcion") not in _PAID_PLANS:
        return fail("Los Credit Packs requieren un plan pago (basic/pro/enterprise)", "requires_paid_plan")

    credits_row = supabase.client.table("client_agent_credits").select("packs").eq("client_id", client_id).execute()
    existing_packs = (credits_row.data[0].get("packs") if credits_row.data else None) or []
    if has_active_credit_pack(existing_packs):
        return fail("Ya tenés un Credit Pack activo · cancelá el actual primero", "already_active")

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
        metadata={"client_id": client_id, "credit_pack_code": credit_pack_code},
    )
    logger.info(f"Credit Pack checkout · cliente {client_id} · pack {credit_pack_code} · session {session.id}")
    return ok({"checkout_url": session.url, "session_id": session.id})
