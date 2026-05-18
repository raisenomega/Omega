"""
Handler: Get Sentinel Status
Retorna último scan de cada agente
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_status() -> Dict[str, Any]:
    """
    Get current security status from latest scans

    Returns:
        Dict with security score, status, and agent details

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Get latest scan for each agent (DISTINCT ON emulation)
        scans_resp = supabase.client.table("sentinel_scans")\
            .select("*")\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()

        scans = scans_resp.data or []

        # Group by agent_code, keep only latest
        latest_by_agent = {}
        for scan in scans:
            agent_code = scan.get("agent_code")
            if agent_code and agent_code not in latest_by_agent:
                latest_by_agent[agent_code] = scan

        # Build agents status dict
        agents_status = {}
        total_issues = 0
        scores = []

        for agent_code, scan in latest_by_agent.items():
            agents_status[agent_code] = {
                "status": scan.get("status", "unknown"),
                "last_run": scan.get("created_at"),
                "issues": len(scan.get("issues", [])),
                "security_score": scan.get("security_score", 0)
            }
            total_issues += len(scan.get("issues", []))
            scores.append(scan.get("security_score", 0))

        # Calculate global score
        global_score = round(sum(scores) / len(scores)) if scores else 0

        # Determine global status
        status = "presidencial" if global_score >= 85 else \
                 "warning" if global_score >= 70 else "critical"

        deploy_decision = "BLOCK" if global_score < 70 else "APPROVE"

        # Collect active issues
        active_issues = []
        for scan in latest_by_agent.values():
            active_issues.extend(scan.get("issues", []))

        logger.info(f"Sentinel status: {status}, score: {global_score}")

        return {
            "security_score": global_score,
            "status": status,
            "last_scan": scans[0].get("created_at") if scans else None,
            "agents": agents_status,
            "deploy_decision": deploy_decision,
            "active_issues": active_issues[:10]  # Top 10 issues
        }

    except Exception as e:
        logger.error(f"Error getting sentinel status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sentinel status: {str(e)}"
        )
