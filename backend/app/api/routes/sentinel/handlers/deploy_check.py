"""
Handler: Deploy Check
Verifica si es seguro deployar ahora
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
from datetime import datetime, timedelta
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_deploy_check() -> Dict[str, Any]:
    """
    Check if it's safe to deploy now

    Returns:
        Dict with deploy decision and reasoning

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get most recent scans
        scans_resp = supabase.client.table("sentinel_scans")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        scans = scans_resp.data or []

        if not scans:
            return {
                "safe_to_deploy": False,
                "decision": "BLOCK",
                "security_score": 0,
                "reason": "No hay scans recientes. Ejecuta un scan primero.",
                "last_scan_age_minutes": None
            }

        # Get latest scan
        latest = scans[0]
        scan_time = datetime.fromisoformat(latest.get("created_at").replace("Z", "+00:00"))
        age_minutes = (datetime.now(scan_time.tzinfo) - scan_time).total_seconds() / 60

        # Calculate average score from recent scans
        recent_scores = [s.get("security_score", 0) for s in scans[:5]]
        avg_score = round(sum(recent_scores) / len(recent_scores)) if recent_scores else 0

        # Decision logic
        safe_to_deploy = True
        decision = "APPROVE"
        reason = "Todos los checks pasaron"

        if avg_score < 70:
            safe_to_deploy = False
            decision = "BLOCK"
            reason = f"Security score muy bajo: {avg_score}/100"
        elif age_minutes > 120:  # Scans older than 2 hours
            safe_to_deploy = False
            decision = "BLOCK"
            reason = f"Último scan hace {round(age_minutes)} minutos. Ejecuta scan actualizado."
        elif avg_score < 85:
            decision = "REVIEW"
            reason = f"Security score moderado: {avg_score}/100. Revisa issues antes de deployar."

        logger.info(f"Deploy check: {decision}, score: {avg_score}")

        return {
            "safe_to_deploy": safe_to_deploy,
            "decision": decision,
            "security_score": avg_score,
            "reason": reason,
            "last_scan_age_minutes": round(age_minutes)
        }

    except Exception as e:
        logger.error(f"Error in deploy check: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check deploy status: {str(e)}"
        )
