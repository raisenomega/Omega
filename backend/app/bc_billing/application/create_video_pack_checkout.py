"""Use case: Stripe Checkout session para activar Video Pack addon.

DEBT-VID-001 · spec §4.4: video_pack_starter ($39) / creator ($95) /
cinematic_pro ($125) recurring monthly. Solo disponible en basic/pro
(Adopción rechazado · spec §4.4 · trial gratis no debe distorsionar funnel).

Policy V1: 1 pack activo por cliente a la vez (más simple · upgrade =
cancel actual primero desde Stripe Customer Portal). Múltiples packs
simultáneos = scope futuro.

Storage: entry se persiste en client_plans.addons jsonb tras webhook
checkout.session.completed → _addon_handlers.handle_video_pack_activation.
Frontend redirect a checkout_url devuelto.
"""
import logging
from app.bc_billing.domain.plan_pricing import (
    VIDEO_PACK_CODES, get_price_id_for_video_pack,
)
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_PAID_PLANS = ("basic", "pro")


def has_active_video_pack(addons: list[dict]) -> bool:
    """True si client_plans.addons tiene cualquier video_pack activo (deactivated_at NULL)."""
    return any(
        a.get("addon_code", "").startswith("video_pack_")
        and a.get("deactivated_at") is None
        for a in (addons or [])
    )


async def create_video_pack_checkout(
    client_id: str, video_pack_code: str, success_url: str, cancel_url: str,
) -> BillingResult:
    """Crea Stripe Checkout para activar Video Pack addon."""
    if video_pack_code not in VIDEO_PACK_CODES:
        return fail(f"video_pack_code inválido: {video_pack_code}", "invalid_video_pack_code")

    price_id = get_price_id_for_video_pack(video_pack_code)
    if price_id is None:
        return fail(f"Stripe Price ID no configurado para video_pack_{video_pack_code}", "price_not_configured")

    supabase = get_supabase_service()
    client_row = supabase.client.table("clients").select(
        "id, name, stripe_customer_id"
    ).eq("id", client_id).execute()
    if not client_row.data:
        return fail(f"Cliente {client_id} no encontrado", "client_not_found")
    client = client_row.data[0]

    plan_row = supabase.client.table("client_plans").select("plan, addons").eq("client_id", client_id).execute()
    if not plan_row.data:
        return fail(f"client_plans row no existe para {client_id}", "client_plans_missing")
    plan_data = plan_row.data[0]
    current_plan = plan_data.get("plan") or "adopcion"
    if current_plan not in _PAID_PLANS:
        return fail(
            f"Video Packs requieren plan basic/pro · actual: {current_plan}",
            "requires_paid_plan",
        )
    addons = plan_data.get("addons") or []
    if has_active_video_pack(addons):
        return fail("Ya tenés un Video Pack activo · cancelá el actual primero", "already_active")

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
        metadata={"client_id": client_id, "video_pack_code": video_pack_code},
    )
    logger.info(f"Video Pack checkout · cliente {client_id} · pack {video_pack_code} · session {session.id}")
    return ok({"checkout_url": session.url, "session_id": session.id})
