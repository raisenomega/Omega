"""Use case: procesar Stripe webhook event con idempotencia X4.

Flujo:
1. Verify signature via stripe_adapter (rechaza requests forged)
2. Idempotency check: si event_id ya está en webhook_events → skip
3. INSERT event en webhook_events (audit forensics)
4. Dispatch al handler apropiado por event_type (privado en _webhook_handlers)
5. Errors en handler NO bloquean idempotencia (event queda registrado)
"""
import logging
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.bc_billing.infrastructure.stripe_adapter import get_stripe_adapter
from app.bc_billing.application._webhook_handlers import EVENT_HANDLERS
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.infrastructure.hermes_usage import record_mcp_use  # HERMES f1.5 · usage-tracking

logger = logging.getLogger(__name__)


async def process_stripe_event(raw_payload: bytes, signature: str) -> BillingResult:
    adapter = get_stripe_adapter()
    try:
        event = adapter.verify_and_construct_event(raw_payload, signature)
    except Exception as e:
        record_mcp_use("stripe", ok=False, detail=str(e)[:80])  # HERMES f1.5 · firma inválida/Stripe problema
        logger.warning(f"Webhook signature verification failed: {e}")
        return fail(f"Invalid signature: {e}", "invalid_signature")

    record_mcp_use("stripe", ok=True)  # HERMES f1.5 · evento válido = Stripe vivo (antes del idempotent-skip)
    event_id, event_type = event["id"], event["type"]
    supabase = get_supabase_service()

    existing = supabase.client.table("webhook_events").select("id").eq(
        "event_id", event_id
    ).execute()
    if existing.data:
        logger.info(f"Webhook {event_id} ya procesado · idempotent skip")
        return ok({"idempotent_skip": True, "event_id": event_id})

    supabase.client.table("webhook_events").insert({
        "provider": "stripe",
        "event_id": event_id,
        "event_type": event_type,
        "payload": dict(event),
    }).execute()
    logger.info(f"Webhook registrado · {event_id} · {event_type}")

    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        try:
            await handler(event, supabase)
        except Exception as e:
            logger.error(f"Handler error en {event_type}: {e}", exc_info=True)
            return fail(f"Handler failed: {e}", "handler_error")
    else:
        logger.info(f"Sin handler para event_type={event_type} · solo audit")

    return ok({"event_id": event_id, "event_type": event_type})
