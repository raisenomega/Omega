"""Handlers internos del webhook dispatcher. Privado · usado solo por process_webhook."""
import logging
from datetime import datetime, timedelta, timezone
from app.bc_billing.application._addon_handlers import handle_addon_deactivation
from app.bc_billing.application._checkout_dispatch import dispatch_addon_or_pack
from app.bc_billing.application._webhook_helpers import (
    _lookup_client_by_customer, _iso_from_ts, _now_iso, sync_subscription,
)
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


async def on_checkout_completed(event: dict, supabase: SupabaseService) -> None:
    """Plan upgrade (target_plan) o delega addon/video/credit-pack a dispatch_addon_or_pack."""
    session = event["data"]["object"]
    metadata = session.get("metadata", {})
    sub_id = session.get("subscription")
    if await dispatch_addon_or_pack(metadata, sub_id, supabase):
        return
    client_id = metadata.get("client_id")
    customer_id = session.get("customer")
    target_plan = metadata.get("target_plan")
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
    """DEBT-076 · sync period_end + sub_id + plan (aplica downgrades programados
    cuando Stripe SubscriptionSchedule cambia de fase al fin de ciclo)."""
    sub = event["data"]["object"]
    client = _lookup_client_by_customer(supabase, sub.get("customer"))
    if not client:
        return
    sync_subscription(supabase, client["id"], sub)


async def on_subscription_deleted(event: dict, supabase: SupabaseService) -> None:
    """Si la sub es de un addon → handle_addon_deactivation. Else plan downgrade → Adopción 7d."""
    sub = event["data"]["object"]
    # DEBT-037: probar primero si es addon (lookup por subscription_id en addons jsonb)
    if await handle_addon_deactivation(sub.get("id"), supabase):
        return
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


EVENT_HANDLERS = {
    "checkout.session.completed": on_checkout_completed,
    "customer.subscription.updated": on_subscription_updated,
    "customer.subscription.deleted": on_subscription_deleted,
}
