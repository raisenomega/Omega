"""DEBT-046 · ARIA Premium reseller billing.

Extraído de _addon_handlers / create_aria_premium_checkout para mantener
esos archivos ≤100L (C4). Reseller path: aria_premium_reseller ($25/mes ·
sube resellers.aria_level a 4). Storage en resellers.addons jsonb · mismo
lifecycle que el client path pero sobre la tabla resellers.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from app.bc_billing.domain.plan_pricing import get_price_id_for_addon
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.bc_billing.application.create_aria_premium_checkout import has_active_aria_premium
from app.infrastructure.supabase_service import SupabaseService, get_supabase_service

logger = logging.getLogger(__name__)

_RESELLER_BASE_LEVEL = 3  # resellers default sin addon
_VALID_ADDONS_RESELLER = ("aria_premium_reseller",)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def handle_reseller_addon_activation(
    reseller_id: str, addon_code: str, subscription_id: str,
    supabase: SupabaseService,
) -> None:
    """Push entry a resellers.addons + bump resellers.aria_level (max 4)."""
    row = supabase.client.table("resellers").select("addons, aria_level").eq("id", reseller_id).execute()
    addons = (row.data[0].get("addons") if row.data else None) or []
    current = (row.data[0].get("aria_level") if row.data else _RESELLER_BASE_LEVEL) or _RESELLER_BASE_LEVEL
    addons.append({
        "addon_code": addon_code, "stripe_subscription_id": subscription_id,
        "activated_at": _now_iso(), "deactivated_at": None,
    })
    new_level = min(current + 1, 4)
    supabase.client.table("resellers").update(
        {"addons": addons, "aria_level": new_level}
    ).eq("id", reseller_id).execute()
    logger.info(f"ARIA Premium activated · reseller={reseller_id} · aria_level {current}→{new_level}")


async def deactivate_reseller_addon(
    subscription_id: str, supabase: SupabaseService,
) -> Optional[str]:
    """Match addon por subscription_id en resellers.addons · marca deactivated_at
    + reset aria_level a base. Retorna reseller id si match."""
    resellers = supabase.client.table("resellers").select("id, addons").execute()
    for r in (resellers.data or []):
        for a in (r.get("addons") or []):
            if a.get("stripe_subscription_id") == subscription_id and a.get("deactivated_at") is None:
                a["deactivated_at"] = _now_iso()
                supabase.client.table("resellers").update(
                    {"addons": r["addons"], "aria_level": _RESELLER_BASE_LEVEL}
                ).eq("id", r["id"]).execute()
                logger.info(f"ARIA Premium deactivated · reseller={r['id']} · aria_level reset to {_RESELLER_BASE_LEVEL}")
                return r["id"]
    return None


async def create_aria_premium_reseller_checkout(
    reseller_id: str, addon_code: str, success_url: str, cancel_url: str,
) -> BillingResult:
    """Stripe Checkout para activar ARIA Premium reseller ($25/mes)."""
    if addon_code not in _VALID_ADDONS_RESELLER:
        return fail(f"addon_code inválido para reseller: {addon_code}", "invalid_addon_code")
    price_id = get_price_id_for_addon(addon_code)
    if price_id is None:
        return fail(f"Stripe Price ID no configurado para {addon_code}", "price_not_configured")
    supabase = get_supabase_service()
    row = supabase.client.table("resellers").select("id, name, stripe_customer_id, addons").eq("id", reseller_id).execute()
    if not row.data:
        return fail(f"Reseller {reseller_id} no encontrado", "reseller_not_found")
    reseller = row.data[0]
    if has_active_aria_premium(reseller.get("addons") or []):
        return fail("ARIA Premium ya activo para este reseller", "already_active")
    adapter = get_stripe_adapter()
    stripe_customer_id = reseller.get("stripe_customer_id")
    if not stripe_customer_id:
        customer = adapter.create_customer(
            metadata={"reseller_id": reseller_id, "reseller_name": reseller.get("name") or ""}
        )
        stripe_customer_id = customer.id
        supabase.client.table("resellers").update(
            {"stripe_customer_id": stripe_customer_id}
        ).eq("id", reseller_id).execute()
    session = adapter.create_checkout_session(
        customer_id=stripe_customer_id, price_id=price_id,
        success_url=success_url, cancel_url=cancel_url,
        metadata={"reseller_id": reseller_id, "addon_code": addon_code},
    )
    logger.info(f"ARIA Premium checkout · reseller {reseller_id} · session {session.id}")
    return ok({"checkout_url": session.url, "session_id": session.id})
