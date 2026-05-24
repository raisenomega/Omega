"""Handlers internos para eventos de addons (no plan upgrades).

DEBT-037 V1 · branched desde _webhook_handlers.on_checkout_completed cuando
metadata.addon_code presente. Push entry a client_plans.addons jsonb +
bump clients.aria_level (LEAST + 1, 4). Deactivation: mark deactivated_at +
reset aria_level a base_level_for_plan.

Lookup deactivation: scan O(N) de client_plans.addons[*].stripe_subscription_id.
V1 OK para <1000 clients · futuro: index gin sobre addons o tabla separada.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)

_BASE_LEVEL = {"adopcion": 1, "basic": 2, "pro": 3, "enterprise": 4}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def handle_addon_activation(
    client_id: str, addon_code: str, subscription_id: str,
    supabase: SupabaseService,
) -> None:
    """Push entry a client_plans.addons + bump clients.aria_level (max 4)."""
    plan_row = supabase.client.table("client_plans").select("addons").eq("client_id", client_id).execute()
    addons = (plan_row.data[0].get("addons") if plan_row.data else None) or []
    addons.append({
        "addon_code": addon_code, "stripe_subscription_id": subscription_id,
        "activated_at": _now_iso(), "deactivated_at": None,
    })
    supabase.client.table("client_plans").update({"addons": addons}).eq("client_id", client_id).execute()
    client = supabase.client.table("clients").select("aria_level").eq("id", client_id).execute()
    current = (client.data[0].get("aria_level") if client.data else 1) or 1
    new_level = min(current + 1, 4)
    supabase.client.table("clients").update({"aria_level": new_level}).eq("id", client_id).execute()
    logger.info(f"ARIA Premium activated · client={client_id} · aria_level {current}→{new_level}")


async def handle_video_pack_activation(
    client_id: str, video_pack_code: str, subscription_id: str,
    supabase: SupabaseService,
) -> None:
    """DEBT-VID-001 · push entry video_pack a client_plans.addons jsonb.
    NO bumpea aria_level (video pack es cuota de generación · no inteligencia)."""
    plan_row = supabase.client.table("client_plans").select("addons").eq("client_id", client_id).execute()
    addons = (plan_row.data[0].get("addons") if plan_row.data else None) or []
    addons.append({
        "addon_code": f"video_pack_{video_pack_code}",
        "stripe_subscription_id": subscription_id,
        "activated_at": _now_iso(), "deactivated_at": None,
    })
    supabase.client.table("client_plans").update({"addons": addons}).eq("client_id", client_id).execute()
    logger.info(f"Video Pack activated · client={client_id} · pack={video_pack_code}")


async def handle_addon_deactivation(
    subscription_id: str, supabase: SupabaseService,
) -> Optional[str]:
    """Match addon por subscription_id · marca deactivated_at. Reset aria_level
    SOLO si el addon era aria_premium* (video_pack no afecta aria_level · DEBT-VID-001).
    Retorna client_id si match."""
    rows = supabase.client.table("client_plans").select("client_id, plan, addons").execute()
    for r in (rows.data or []):
        for a in (r.get("addons") or []):
            if a.get("stripe_subscription_id") == subscription_id and a.get("deactivated_at") is None:
                a["deactivated_at"] = _now_iso()
                supabase.client.table("client_plans").update(
                    {"addons": r["addons"]}
                ).eq("client_id", r["client_id"]).execute()
                addon_code = a.get("addon_code", "")
                if addon_code.startswith("aria_premium"):
                    base = _BASE_LEVEL.get(r.get("plan") or "adopcion", 1)
                    supabase.client.table("clients").update(
                        {"aria_level": base}
                    ).eq("id", r["client_id"]).execute()
                    logger.info(f"ARIA Premium deactivated · client={r['client_id']} · aria_level reset to {base}")
                else:
                    logger.info(f"Addon {addon_code} deactivated · client={r['client_id']} · aria_level intacto")
                return r["client_id"]
    return None
