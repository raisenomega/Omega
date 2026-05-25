"""
Sentinel Router - Security & Monitoring
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query, Header
from typing import Optional

from .handlers import (
    handle_get_status,
    handle_run_scan,
    handle_get_history,
    handle_deploy_check,
    ScanRequest
)

router = APIRouter(prefix="/sentinel", tags=["SENTINEL 🛡️"])


@router.get("/status/")
async def get_status(authorization: Optional[str] = Header(None)):
    """Get current security status · solo owner/superadmin (4B-5)."""
    return await handle_get_status(authorization)


@router.post("/scan/")
async def run_scan(request: ScanRequest, authorization: Optional[str] = Header(None)):
    """Execute security scan (vault | pulse | db | full) · solo superadmin (4B-5)."""
    return await handle_run_scan(request, authorization)


@router.get("/history/")
async def get_history(
    limit: int = Query(default=30, description="Number of records"),
    agent_code: Optional[str] = Query(None, description="Filter by agent"),
    authorization: Optional[str] = Header(None),
):
    """Get scan history · solo superadmin (4B-5)."""
    return await handle_get_history(authorization, limit, agent_code)


@router.get("/deploy-check/")
async def deploy_check(authorization: Optional[str] = Header(None)):
    """Check if it's safe to deploy now · solo superadmin (4B-5)."""
    return await handle_deploy_check(authorization)
