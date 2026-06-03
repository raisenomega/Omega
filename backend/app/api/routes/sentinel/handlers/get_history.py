"""
Handler: Get Scan History
Retorna historial de scans con paginación
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin
from app.services.sentinel_helpers import issue_hash

logger = logging.getLogger(__name__)


def _attach_previous_actions(supabase, scans: list) -> None:
    """Joinea cada issue con sus acciones previas (Ignorar/Fix) vía issue_hash · best-effort."""
    hashes = [
        issue_hash(it.get("severity", ""), it.get("type", ""), it.get("message", ""))
        for s in scans for it in (s.get("issues") or [])
    ]
    actions_by_hash: Dict[str, list] = {}
    if hashes:
        try:
            resp = supabase.client.table("sentinel_issue_actions")\
                .select("issue_hash,action,reason,created_at")\
                .in_("issue_hash", list(set(hashes))).execute()
            for a in (resp.data or []):
                actions_by_hash.setdefault(a["issue_hash"], []).append(
                    {"action": a["action"], "created_at": a["created_at"], "reason": a.get("reason")}
                )
        except Exception as e:
            logger.warning(f"issue actions join failed (best-effort): {e}")
    for s in scans:
        for it in (s.get("issues") or []):
            h = issue_hash(it.get("severity", ""), it.get("type", ""), it.get("message", ""))
            it["previous_actions"] = actions_by_hash.get(h, [])


async def handle_get_history(authorization: Optional[str], limit: int = 30, agent_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Get scan history with pagination · solo owner/superadmin (4B-5 · SENTINEL es del sistema).

    Raises:
        HTTPException 401/403: sin auth / no superadmin · 500: Database error
    """
    await require_superadmin(authorization)
    try:
        supabase = get_supabase_service()

        # Build query
        query = supabase.client.table("sentinel_scans")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(min(limit, 100))  # Max 100

        # Filter by agent if provided
        if agent_code:
            query = query.eq("agent_code", agent_code.upper())

        # Execute query
        resp = query.execute()
        scans = resp.data or []

        # Join acciones previas (Ignorar/Fix) por issue_hash → it["previous_actions"].
        _attach_previous_actions(supabase, scans)

        logger.info(f"Retrieved {len(scans)} scan records")

        return {
            "total": len(scans),
            "scans": scans,
            "filtered_by": agent_code if agent_code else "all"
        }

    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get scan history: {str(e)}"
        )
