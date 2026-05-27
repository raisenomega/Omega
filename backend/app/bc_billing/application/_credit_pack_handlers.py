"""DEBT-052 FASE 4 · enrolamiento al comprar un Credit Pack (webhook).

checkout.session.completed con metadata.credit_pack_code → UPSERT en
client_agent_credits: fija el budget mensual del tier (PACK_BUDGETS_USD), resetea
consumido, abre periodo (now → +30d) y registra el pack en packs jsonb
{tier, stripe_subscription_id, auto_recharge:false} (toggle de auto-recarga · 5/5).
Idempotencia X4 garantizada aguas arriba por process_webhook (webhook_events).
"""
import logging
from datetime import datetime, timedelta, timezone
from app.infrastructure.supabase_service import SupabaseService
from app.bc_billing.domain.credit_costs import pack_budget_usd

logger = logging.getLogger(__name__)

_PERIOD_DAYS = 30


async def handle_credit_pack_enrollment(
    client_id: str, credit_pack_code: str, subscription_id: str,
    supabase: SupabaseService,
) -> None:
    """UPSERT client_agent_credits: budget del tier + reset consumido + nuevo periodo."""
    budget = pack_budget_usd(credit_pack_code)
    if budget <= 0:
        logger.warning(f"credit pack enrollment con tier desconocido: {credit_pack_code}")
        return
    now = datetime.now(timezone.utc)
    pack_entry = {
        "tier": credit_pack_code,
        "stripe_subscription_id": subscription_id,
        "auto_recharge": False,
        "activated_at": now.isoformat(),
        "deactivated_at": None,
    }
    payload = {
        "client_id": client_id,
        "budget_usd_mensual": budget,
        "consumido_usd": 0,
        "periodo_start": now.isoformat(),
        "periodo_end": (now + timedelta(days=_PERIOD_DAYS)).isoformat(),
        "packs": [pack_entry],
    }
    existing = supabase.client.table("client_agent_credits").select("id").eq("client_id", client_id).execute()
    if existing.data:
        supabase.client.table("client_agent_credits").update(payload).eq("client_id", client_id).execute()
    else:
        supabase.client.table("client_agent_credits").insert(payload).execute()
    logger.info(f"Credit Pack enrollment · client={client_id} · tier={credit_pack_code} · budget=${budget}")
