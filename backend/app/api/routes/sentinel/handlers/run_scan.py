"""
Handler: Run Security Scan
Ejecuta scans de seguridad y guarda resultados
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel
import logging

from app.services.sentinel_service import SentinelService
from app.api.routes.auth.auth_utils import require_superadmin

logger = logging.getLogger(__name__)


class ScanRequest(BaseModel):
    scan_type: str  # "vault" | "pulse" | "db" | "full"


async def handle_run_scan(request: ScanRequest, authorization: Optional[str]) -> Dict[str, Any]:
    """
    Execute security scan · solo owner/superadmin (4B-5 · SENTINEL es del sistema).

    Raises:
        HTTPException 401/403: sin auth / no superadmin
        HTTPException 400: Invalid scan type · 500: Scan execution error
    """
    await require_superadmin(authorization)
    try:
        sentinel = SentinelService()

        # Validate scan type
        valid_types = ["vault", "pulse", "db", "full"]
        if request.scan_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scan_type. Must be one of: {valid_types}"
            )

        logger.info(f"Running {request.scan_type} scan...")

        # Execute appropriate scan
        if request.scan_type == "vault":
            result = await sentinel.run_vault_scan()
        elif request.scan_type == "pulse":
            result = await sentinel.run_pulse_monitor()
        elif request.scan_type == "db":
            result = await sentinel.run_db_guardian()
        elif request.scan_type == "full":
            result = await sentinel.run_full_scan()
        else:
            raise HTTPException(status_code=400, detail="Invalid scan type")

        # Save to database if not full scan (full scan saves internally)
        if request.scan_type != "full":
            from app.infrastructure.supabase_service import get_supabase_service
            supabase = get_supabase_service()
            valid_cols = ["agent_code", "scan_type", "status", "security_score", "issues", "deploy_decision", "scan_duration_ms"]
            insert_data = {k: v for k, v in result.items() if k in valid_cols}
            insert_data["triggered_by"] = "manual"
            supabase.client.table("sentinel_scans").insert(insert_data).execute()

        # Notify NOVA if full scan found issues
        if request.scan_type == "full":
            score  = result.get("security_score", 100)
            issues = result.get("issues", [])
            if score < 100 and issues:
                import time as _time
                from app.infrastructure.supabase_service import get_supabase_service
                _db = get_supabase_service()
                critical = [i for i in issues if i["severity"] == "CRITICAL"]
                high     = [i for i in issues if i["severity"] == "HIGH"]
                summary  = "; ".join(f"{i['type']}: {i['message']}" for i in issues[:5])

                # 1 — omega_activity: NOVA se entera
                _db.client.table("omega_activity").insert({
                    "id":         f"sentinel_alert_{int(_time.time())}",
                    "client_id":  None,
                    "agent_code": "SENTINEL",
                    "type":       "security_alert",
                    "content":    f"SENTINEL score {score}/100. {len(issues)} issue(s): {summary}",
                    "metadata": {
                        "score":          score,
                        "issues_count":   len(issues),
                        "critical_count": len(critical),
                        "high_count":     len(high),
                        "needs_action":   True,
                    },
                }).execute()

                # 2 — omega_approval_requests si hay CRITICAL
                if critical:
                    detail = "; ".join(f"{i['type']}: {i['message']}" for i in critical)
                    _db.client.table("omega_approval_requests").insert({
                        "id":         f"sentinel_critical_{int(_time.time())}",
                        "client_id":  None,
                        "agent_code": "SENTINEL",
                        "type":       "security_critical",
                        "urgency":    "critical",
                        "content":    detail,
                        "status":     "pending",
                    }).execute()

        logger.info(f"{request.scan_type} scan completed: score={result.get('security_score', 0)}")

        return {
            "success": True,
            "scan_type": request.scan_type,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running scan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run scan: {str(e)}"
        )
