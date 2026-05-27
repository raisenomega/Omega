"""Handlers internos del webhook dispatcher. Privado · usado solo por process_webhook."""
import logging
from datetime import datetime, timedelta, timezone
from app.bc_billing.application._addon_handlers import handle_addon_activation, handle_addon_deactivation, handle_video_pack_activation
from app.bc_billing.application.reseller_aria import handle_reseller_addon_activation
from app.bc_billing.application._webhook_helpers import (
    _lookup_client_by_customer, _iso_from_ts, _now_iso,
)
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


async def on_checkout_completed(event: dict, supabase: SupabaseService) -> None:
    """Persistir plan upgrade (target_plan) o addon activation (addon_code) según metadata."""
    session = event["data"]["object"]
    metadata = session.get("metadata", {})
    client_id = metadata.get("client_id")
    sub_id = session.get("subscription")
    customer_id = session.get("customer")
    addon_code = metadata.get("addon_code")
    video_pack_code = metadata.get("video_pack_code")
    reseller_id = metadata.get("reseller_id")
    if addon_code:  # DEBT-046: reseller addon → handler dedicado; client → handler original
        if addon_code == "aria_premium_reseller":
            if not all([reseller_id, sub_id]):
                logger.warning(f"reseller addon checkout.completed con data faltante: {session.get('id')}")
                return
            await handle_reseller_addon_activation(reseller_id, addon_code, sub_id, supabase)
        else:
            if not all([client_id, sub_id]):
                logger.warning(f"addon checkout.completed con data faltante: {session.get('id')}")
                return
            await handle_addon_activation(client_id, addon_code, sub_id, supabase)
        return
    if video_pack_code:
        if not all([client_id, sub_id, video_pack_code]):
            logger.warning(f"video_pack checkout.completed con data faltante: {session.get('id')}")
            return
        await handle_video_pack_activation(client_id, video_pack_code, sub_id, supabase)
        return
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
