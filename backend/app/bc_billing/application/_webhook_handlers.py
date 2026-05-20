"""Handlers internos del webhook dispatcher. Privado · usado solo por process_webhook."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


async def on_checkout_completed(event: dict, supabase: SupabaseService) -> None:
    """Persistir clients.stripe_customer_id + client_plans con plan target."""
    session = event["data"]["object"]
    client_id = session.get("metadata", {}).get("client_id")
    target_plan = session.get("metadata", {}).get("target_plan")
    sub_id = session.get("subscription")
    customer_id = session.get("customer")
    if not all([client_id, target_plan, sub_id, customer_id]):
        logger.warning(f"checkout.session.completed con data faltante: {session.get('id')}")
        return

    subscription = get_stripe_adapter().retrieve_subscription(sub_id)
    period_end = _iso_from_ts(subscription["current_period_end"])

    supabase.client.table("clients").update(
        {"stripe_customer_id": customer_id, "plan": target_plan}
    ).eq("id", client_id).execute()

    supabase.client.table("client_plans").update({
        "plan": target_plan,
        "current_period_start": _now_iso(),
        "current_period_end": period_end,
        "stripe_subscription_id": sub_id,
    }).eq("client_id", client_id).execute()
    logger.info(f"Cliente {client_id} activado · plan={target_plan} · renueva {period_end}")


async def on_subscription_updated(event: dict, supabase: SupabaseService) -> None:
    """Sync current_period_end + stripe_subscription_id ante renewal/cambio."""
    sub = event["data"]["object"]
    client = _lookup_client_by_customer(supabase, sub.get("customer"))
    if not client:
        return
    supabase.client.table("client_plans").update({
        "current_period_end": _iso_from_ts(sub["current_period_end"]),
        "stripe_subscription_id": sub["id"],
    }).eq("client_id", client["id"]).execute()


async def on_subscription_deleted(event: dict, supabase: SupabaseService) -> None:
    """Downgrade graceful → Adopción 7d (decisión #2 · spec §3)."""
    sub = event["data"]["object"]
    client = _lookup_client_by_customer(supabase, sub.get("customer"))
    if not client:
        return
    now = datetime.now(timezone.utc)
    supabase.client.table("clients").update({"plan": "adopcion"}).eq("id", client["id"]).execute()
    supabase.client.table("client_plans").update({
        "plan": "adopcion",
        "current_period_start": now.isoformat(),
        "current_period_end": (now + timedelta(days=7)).isoformat(),
        "stripe_subscription_id": None,
    }).eq("client_id", client["id"]).execute()
    logger.info(f"Cliente {client['id']} downgraded → Adopción 7d (subscription canceled)")


def _lookup_client_by_customer(supabase: SupabaseService, customer_id: Optional[str]) -> Optional[dict]:
    if not customer_id:
        return None
    r = supabase.client.table("clients").select("id").eq("stripe_customer_id", customer_id).execute()
    return r.data[0] if r.data else None


def _iso_from_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


EVENT_HANDLERS = {
    "checkout.session.completed": on_checkout_completed,
    "customer.subscription.updated": on_subscription_updated,
    "customer.subscription.deleted": on_subscription_deleted,
}
