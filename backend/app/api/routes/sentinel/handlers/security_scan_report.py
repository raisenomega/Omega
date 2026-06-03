"""Handlers Capa 4: receptor del reporte de dependency scan (GitHub Action) + lectura del último.

POST receiver = auth machine-to-machine (X-Sentinel-Token constante-time · NO require_superadmin).
GET latest = owner-only (require_superadmin) para el panel.
"""
import os
import hmac
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin

logger = logging.getLogger(__name__)


class SecurityScanReport(BaseModel):
    scan_type: str
    status: str
    run_id: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None


def _valid_token(provided: Optional[str]) -> bool:
    """Comparación constante-time contra SENTINEL_TOKEN (os.getenv · patrón sentinel_pulse)."""
    expected = os.getenv("SENTINEL_TOKEN", "")
    if not expected or not provided:
        return False
    return hmac.compare_digest(provided, expected)


async def handle_security_scan_report(request: SecurityScanReport, x_sentinel_token: Optional[str]) -> Dict[str, Any]:
    """Recibe el reporte del runner de GitHub · persiste en sentinel_dependency_scans."""
    if not _valid_token(x_sentinel_token):
        raise HTTPException(status_code=401, detail="Invalid SENTINEL token")
    supabase = get_supabase_service()
    resp = supabase.client.table("sentinel_dependency_scans").insert({
        "scan_type": request.scan_type,
        "status": request.status,
        "summary": request.summary or {},
        "github_run_id": request.run_id,
    }).execute()
    rec_id = (resp.data or [{}])[0].get("id")
    logger.info(f"dependency scan report: {request.scan_type}={request.status} run={request.run_id}")
    return {"received": True, "scan_record_id": rec_id}


async def handle_get_latest_dependency_scan(authorization: Optional[str]) -> Dict[str, Any]:
    """Último dependency scan para el panel SENTINEL · owner-only."""
    await require_superadmin(authorization)
    supabase = get_supabase_service()
    resp = supabase.client.table("sentinel_dependency_scans")\
        .select("*").order("created_at", desc=True).limit(1).execute()
    return {"latest": (resp.data or [None])[0]}
