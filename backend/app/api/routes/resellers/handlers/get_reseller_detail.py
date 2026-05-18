"""
Handler: Reseller Detail
GET /resellers/{reseller_id}/ - Full reseller profile with stats
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_reseller_detail(reseller_id: str) -> Dict[str, Any]:
    """
    Get full reseller detail including clients count and MRR

    Args:
        reseller_id: Reseller UUID

    Returns:
        Dict with reseller data and calculated stats

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get reseller
        reseller_resp = supabase.client.table("resellers")\
            .select("*")\
            .eq("id", reseller_id)\
            .single()\
            .execute()

        if not reseller_resp.data:
            raise HTTPException(status_code=404, detail="Reseller not found")

        reseller = reseller_resp.data

        # Count clients
        clients_resp = supabase.client.table("clients")\
            .select("id", count="exact")\
            .eq("reseller_id", reseller_id)\
            .execute()

        clients_count = clients_resp.count or 0

        # Calculate MRR (simplified - would need subscription data in production)
        mrr_generated = reseller.get("monthly_revenue_reported", 0)

        return {
            "id": reseller.get("id"),
            "agency_name": reseller.get("agency_name"),
            "contact_name": reseller.get("owner_name") or reseller.get("contact_name"),
            "email": reseller.get("owner_email") or reseller.get("email"),
            "phone": reseller.get("phone"),
            "plan": reseller.get("plan", "starter"),
            "status": reseller.get("status", "active"),
            "commission_rate": reseller.get("omega_commission_rate", 30),
            "created_at": reseller.get("created_at"),
            "clients_count": clients_count,
            "mrr_generated": mrr_generated
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reseller detail: {str(e)}")
