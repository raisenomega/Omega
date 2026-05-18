"""
Handler: Reseller Stats
GET /resellers/{reseller_id}/stats/ - Performance metrics
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_get_reseller_stats(reseller_id: str) -> Dict[str, Any]:
    """Get performance metrics for this reseller"""
    try:
        supabase = get_supabase_service()
        # Get reseller
        reseller_resp = supabase.client.table("resellers")\
            .select("omega_commission_rate, monthly_revenue_reported")\
            .eq("id", reseller_id).single().execute()
        if not reseller_resp.data:
            raise HTTPException(status_code=404, detail="Reseller not found")
        reseller = reseller_resp.data
        # Get clients with status breakdown
        clients_resp = supabase.client.table("clients")\
            .select("status, plan").eq("reseller_id", reseller_id).execute()
        clients = clients_resp.data or []
        total = len(clients)
        active = len([c for c in clients if c.get("status") == "active"])
        trial = len([c for c in clients if c.get("subscription_status") == "trial"])
        inactive = total - active
        mrr = reseller.get("monthly_revenue_reported", 0)
        commission_rate = reseller.get("omega_commission_rate", 30)
        commission = mrr * commission_rate / 100
        # Most common plan
        plans = [c.get("plan") for c in clients if c.get("plan")]
        avg_plan = max(set(plans), key=plans.count) if plans else "basic"
        return {
            "clients_total": total, "clients_active": active, "clients_trial": trial,
            "mrr_generated": mrr, "commission_earned": commission,
            "churn_rate": round((inactive / total * 100) if total > 0 else 0, 2),
            "avg_client_plan": avg_plan, "top_client": {"name": "N/A", "plan": "N/A"}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reseller stats: {str(e)}")
