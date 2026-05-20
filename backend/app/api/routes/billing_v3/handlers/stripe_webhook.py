"""POST /billing/webhook · Stripe webhook · delega a bc_billing.application.

Importante: Stripe espera respuesta 2xx en <30s o reintenta. Por eso:
- Idempotency check garantiza que retry no re-procese (X4)
- handler_error retorna 500 → Stripe reintenta (idempotencia lo cubre)
- invalid_signature retorna 400 → rechaza forgeries
- success (incluido idempotent_skip) retorna 200 → Stripe deja de reintentar
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from app.bc_billing.application.process_webhook import process_stripe_event

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def stripe_webhook_endpoint(request: Request) -> dict:
    """Procesa eventos Stripe con signature verification + idempotencia.

    Eventos manejados:
    - checkout.session.completed → upsert client_plans + clients.stripe_customer_id
    - customer.subscription.updated → sync current_period_end
    - customer.subscription.deleted → downgrade graceful Adopción 7d
    Otros eventos quedan en webhook_events (audit) sin handler dedicado.
    """
    raw_payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    result = await process_stripe_event(raw_payload, signature)

    if result.get("success"):
        return {"received": True, "idempotent": bool((result.get("data") or {}).get("idempotent_skip"))}

    error_code = result.get("error_code") or "billing_error"
    error_msg = result.get("error") or "Unknown webhook error"

    if error_code == "invalid_signature":
        raise HTTPException(status_code=400, detail=error_msg)

    # handler_error → 500 · Stripe reintenta · idempotencia X4 protege
    logger.error(f"Webhook handler failed · {error_code} · {error_msg}")
    raise HTTPException(status_code=500, detail=error_msg)
