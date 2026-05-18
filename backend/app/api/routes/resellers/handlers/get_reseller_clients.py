"""
Handler: Reseller Clients
GET /resellers/{reseller_id}/clients/ - List clients for reseller
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_reseller_clients(reseller_id: str) -> Dict[str, Any]:
    """
    Get list of clients for this reseller

    Args:
        reseller_id: Reseller UUID

    Returns:
        Dict with clients array and total count

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Verify reseller exists
        reseller_resp = supabase.client.table("resellers")\
            .select("id")\
            .eq("id", reseller_id)\
            .single()\
            .execute()

        if not reseller_resp.data:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Get clients
        clients_resp = supabase.client.table("clients")\
            .select("*")\
            .eq("reseller_id", reseller_id)\
            .order("created_at.desc")\
            .execute()

        clients_data = clients_resp.data or []
        clients = [
            {
                "id": client.get("id"),
                "name": client.get("name"),
                "business_name": client.get("company"),
                "plan": client.get("plan"),
                "status": client.get("status"),
                "created_at": client.get("created_at")
            }
            for client in clients_data
        ]

        return {"clients": clients, "total": len(clients)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller clients: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reseller clients: {str(e)}")
