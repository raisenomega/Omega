"""
Handler: Reseller Activity
GET /resellers/{reseller_id}/activity/ - Activity feed
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_get_reseller_activity(reseller_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """Get recent activity for this reseller"""
    try:
        supabase = get_supabase_service()
        # Verify reseller exists
        reseller_resp = supabase.client.table("resellers")\
            .select("id").eq("id", reseller_id).single().execute()
        if not reseller_resp.data:
            raise HTTPException(status_code=404, detail="Reseller not found")
        # Get recent clients as activity proxy
        clients_resp = supabase.client.table("clients")\
            .select("name, company, plan, status, created_at", count="exact")\
            .eq("reseller_id", reseller_id).order("created_at.desc")\
            .range(offset, offset + limit - 1).execute()
        clients_data = clients_resp.data or []
        activities = [
            {
                "type": "client_added",
                "description": f"Nuevo cliente añadido: {client.get('name', 'N/A')}",
                "client_name": client.get("name") or client.get("company"),
                "timestamp": client.get("created_at")
            }
            for client in clients_data
        ]
        return {"activities": activities, "total": clients_resp.count or 0}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller activity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reseller activity: {str(e)}")
