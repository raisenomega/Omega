"""DEBT-091 · activación de Agent Add-On (webhook checkout.session.completed).

Push entry agent_<code> a client_plans.addons jsonb. NO bumpea aria_level (igual
que video packs · es capacidad de agente, no nivel de inteligencia ARIA). La
desactivación la cubre el handle_addon_deactivation existente (addon_code no
empieza con aria_premium → no resetea aria_level).
"""
import logging
from datetime import datetime, timezone
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


async def handle_agent_addon_activation(
    client_id: str, agent_addon_code: str, subscription_id: str,
    supabase: SupabaseService,
) -> None:
    """Push entry agent_<code> a client_plans.addons jsonb."""
    plan_row = supabase.client.table("client_plans").select("addons").eq("client_id", client_id).execute()
    addons = (plan_row.data[0].get("addons") if plan_row.data else None) or []
    addons.append({
        "addon_code": f"agent_{agent_addon_code}",
        "stripe_subscription_id": subscription_id,
        "activated_at": datetime.now(timezone.utc).isoformat(),
        "deactivated_at": None,
    })
    supabase.client.table("client_plans").update({"addons": addons}).eq("client_id", client_id).execute()
    logger.info(f"Agent Add-On activated · client={client_id} · agent={agent_addon_code}")
