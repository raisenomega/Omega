"""DEBT-076 · programa downgrade de plan a fin de ciclo (Stripe SubscriptionSchedule).

El cambio NO es inmediato: Stripe aplica el nuevo precio al current_period_end.
El webhook customer.subscription.updated sincroniza clients.plan al aplicarse
(plan_for_price_id). Si STRIPE_PRICE_<plan> no está configurado → 503 honesto.
"""
import logging
from app.bc_billing.domain.plan_pricing import get_price_id_for_plan, is_valid_downgrade
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def schedule_plan_downgrade(client_id: str, target_plan: str) -> BillingResult:
    """Programa el downgrade a target_plan al fin del ciclo actual."""
    price_id = get_price_id_for_plan(target_plan)
    if price_id is None:
        return fail(f"Stripe Price ID no configurado para '{target_plan}'", "price_not_configured")

    supabase = get_supabase_service()
    row = (
        supabase.client.table("client_plans")
        .select("client_id, plan, stripe_subscription_id")
        .eq("client_id", client_id)
        .execute()
    )
    if not row.data:
        return fail(f"client_plans {client_id} no encontrado", "client_not_found")
    cp = row.data[0]
    if not is_valid_downgrade(cp["plan"], target_plan):
        return fail(f"Downgrade inválido: {cp['plan']} → {target_plan}", "invalid_downgrade_path")
    sub_id = cp.get("stripe_subscription_id")
    if not sub_id:
        return fail("Sin subscription Stripe activa para programar el downgrade", "no_active_subscription")

    schedule = get_stripe_adapter().schedule_downgrade_at_period_end(sub_id, price_id)
    logger.info(f"Downgrade programado · client={client_id} · {cp['plan']}→{target_plan} · schedule={schedule.id}")
    return ok({"scheduled": True, "schedule_id": schedule.id, "target_plan": target_plan})
