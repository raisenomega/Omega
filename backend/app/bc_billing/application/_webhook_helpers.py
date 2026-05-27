"""Helpers stateless del webhook dispatcher. Privado · split de _webhook_handlers (C4)."""
from datetime import datetime, timezone
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService
from app.bc_billing.domain.plan_pricing import plan_for_price_id


def _lookup_client_by_customer(supabase: SupabaseService, customer_id: Optional[str]) -> Optional[dict]:
    if not customer_id:
        return None
    r = supabase.client.table("clients").select("id").eq("stripe_customer_id", customer_id).execute()
    return r.data[0] if r.data else None


def _iso_from_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync_subscription(supabase: SupabaseService, client_id: str, sub: dict) -> None:
    """DEBT-076 · sync period_end + sub_id + plan. El precio activo de la sub →
    plan (plan_for_price_id) aplica el downgrade programado cuando Stripe cambia
    de fase. Si el precio no mapea a un plan (addon/video sub) → no toca el plan."""
    updates = {
        "current_period_end": _iso_from_ts(sub["current_period_end"]),
        "stripe_subscription_id": sub["id"],
    }
    items = (sub.get("items") or {}).get("data") or []
    price_id = (items[0].get("price") or {}).get("id") if items else None
    new_plan = plan_for_price_id(price_id) if price_id else None
    if new_plan:
        updates["plan"] = new_plan
        supabase.client.table("clients").update({"plan": new_plan}).eq("id", client_id).execute()
    supabase.client.table("client_plans").update(updates).eq("client_id", client_id).execute()
