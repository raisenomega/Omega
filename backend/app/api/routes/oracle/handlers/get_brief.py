"""
Handler: Get ORACLE Brief
GET /oracle/brief/ - Retorna último intelligence brief
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service
from app.services.oracle_service import OracleService

logger = logging.getLogger(__name__)


async def handle_get_brief() -> Dict[str, Any]:
    """
    Get latest ORACLE Intelligence Brief
    Si no existe → genera uno nuevo automáticamente

    Returns:
        Dict with intelligence brief data

    Raises:
        HTTPException 500: Database or generation error
    """
    try:
        supabase = get_supabase_service()

        # Buscar último brief en nova_data
        brief_resp = supabase.client.table("nova_data")\
            .select("content, updated_at")\
            .eq("user_id", "ibrain")\
            .eq("data_type", "oracle_brief")\
            .single()\
            .execute()

        if brief_resp.data and brief_resp.data.get("content"):
            return {
                "success": True,
                "brief": brief_resp.data["content"],
                "last_updated": brief_resp.data.get("updated_at"),
                "source": "cached"
            }

        # Si no hay brief → generar uno nuevo
        logger.info("No ORACLE brief found, generating new one...")
        oracle = OracleService()
        new_brief = await oracle.generate_intelligence_brief()

        return {
            "success": True,
            "brief": new_brief,
            "last_updated": new_brief.get("generated_at"),
            "source": "generated"
        }

    except Exception as e:
        logger.error(f"Error getting ORACLE brief: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ORACLE brief: {str(e)}")
