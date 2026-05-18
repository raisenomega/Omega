"""
Handler: Client Detail
GET /clients/{client_id}/ - Full client profile with reseller info
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_client_detail(client_id: str) -> Dict[str, Any]:
    """
    Get full client detail including reseller information

    Args:
        client_id: Client UUID

    Returns:
        Dict with client data and reseller info

    Raises:
        HTTPException 404: Client not found
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get client with reseller join
        client_resp = supabase.client.table("clients")\
            .select("*, resellers(agency_name)")\
            .eq("id", client_id)\
            .single()\
            .execute()

        if not client_resp.data:
            raise HTTPException(status_code=404, detail="Client not found")

        client = client_resp.data
        reseller_name = None
        if client.get("resellers") and isinstance(client["resellers"], dict):
            reseller_name = client["resellers"].get("agency_name")

        return {
            "id": client.get("id"),
            "name": client.get("name"),
            "business_name": client.get("company"),
            "email": client.get("email"),
            "phone": client.get("phone"),
            "plan": client.get("plan"),
            "status": client.get("status"),
            "reseller_id": client.get("reseller_id"),
            "reseller_name": reseller_name,
            "created_at": client.get("created_at"),
            "notes": client.get("notes")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client detail: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get client detail: {str(e)}")
