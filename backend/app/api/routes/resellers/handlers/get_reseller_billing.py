"""
Handler: Reseller Billing
GET /resellers/{reseller_id}/billing/ - Subscription and commission data
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging, stripe, os
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
stripe.api_key = os.getenv("STRIPE_API_KEY")

async def handle_get_reseller_billing(reseller_id: str) -> Dict[str, Any]:
    """Get billing information from Stripe or Supabase fallback"""
    try:
        supabase = get_supabase_service()
        # Get reseller with stripe_customer_id
        reseller_resp = supabase.client.table("resellers")\
            .select("id, plan, stripe_customer_id, omega_commission_rate, monthly_revenue_reported")\
            .eq("id", reseller_id).single().execute()
        if not reseller_resp.data:
            raise HTTPException(status_code=404, detail="Reseller not found")
        reseller = reseller_resp.data
        stripe_id = reseller.get("stripe_customer_id")
        commission_rate = reseller.get("omega_commission_rate", 30)
        mrr = reseller.get("monthly_revenue_reported", 0)
        # Try Stripe API if customer exists
        if stripe_id:
            try:
                subs = stripe.Subscription.list(customer=stripe_id, limit=1)
                invoices = stripe.Invoice.list(customer=stripe_id, limit=10)
                sub_data = None
                if subs.data:
                    sub = subs.data[0]
                    sub_data = {
                        "status": sub.status, "plan": reseller.get("plan"),
                        "amount": sub.plan.amount / 100 if sub.plan.amount else 0,
                        "currency": sub.plan.currency or "usd",
                        "current_period_end": sub.current_period_end,
                        "current_period_start": sub.current_period_start,
                        "setup_fee_paid": True
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
                return {
                    "subscription": sub_data, "invoices": invoice_list,
                    "commission": {"rate": commission_rate, "estimated_monthly": mrr * commission_rate / 100}
                }
            except stripe.error.StripeError as e:
                logger.warning(f"Stripe API error for reseller {reseller_id}: {e}")
        # Fallback: return plan data from Supabase
        return {
            "subscription": None, "invoices": [],
            "commission": {"rate": commission_rate, "estimated_monthly": mrr * commission_rate / 100}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller billing: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reseller billing: {str(e)}")
