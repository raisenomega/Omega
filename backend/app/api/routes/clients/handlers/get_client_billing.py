"""
Handler: Client Billing
GET /clients/{client_id}/billing/ - Subscription and invoice data
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging, stripe, os
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
stripe.api_key = os.getenv("STRIPE_API_KEY")

async def handle_get_client_billing(client_id: str) -> Dict[str, Any]:
    """Get billing information from Stripe or Supabase fallback"""
    try:
        supabase = get_supabase_service()
        # Get client with stripe_customer_id
        client_resp = supabase.client.table("clients")\
            .select("id, plan, stripe_customer_id, subscription_status")\
            .eq("id", client_id).single().execute()
        if not client_resp.data:
            raise HTTPException(status_code=404, detail="Client not found")
        client = client_resp.data
        stripe_id = client.get("stripe_customer_id")
        # Try Stripe API if customer exists
        if stripe_id:
            try:
                subs = stripe.Subscription.list(customer=stripe_id, limit=1)
                invoices = stripe.Invoice.list(customer=stripe_id, limit=10)
                sub_data = None
                if subs.data:
                    sub = subs.data[0]
                    sub_data = {
                        "status": sub.status, "plan": client.get("plan"),
                        "amount": sub.plan.amount / 100 if sub.plan.amount else 0,
                        "currency": sub.plan.currency or "usd",
                        "current_period_end": sub.current_period_end,
                        "current_period_start": sub.current_period_start
                    }
                invoice_list = [
                    {
                        "id": inv.id,
                        "amount_paid": inv.amount_paid / 100 if inv.amount_paid else 0,
                        "status": inv.status, "created": inv.created,
                        "invoice_pdf": inv.invoice_pdf
                    }
                    for inv in invoices.data
                ]
                return {"subscription": sub_data, "invoices": invoice_list}
            except stripe.error.StripeError as e:
                logger.warning(f"Stripe API error for client {client_id}: {e}")
        # Fallback: return plan data from Supabase
        return {"subscription": None, "invoices": []}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client billing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get client billing: {str(e)}")
