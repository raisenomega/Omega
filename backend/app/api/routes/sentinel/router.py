"""
Sentinel Router - Security & Monitoring
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query
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
async def get_status():
    """Get current security status from latest scans"""
    return await handle_get_status()


@router.post("/scan/")
async def run_scan(request: ScanRequest):
    """Execute security scan (vault | pulse | db | full)"""
    return await handle_run_scan(request)


@router.get("/history/")
async def get_history(
    limit: int = Query(default=30, description="Number of records"),
    agent_code: Optional[str] = Query(None, description="Filter by agent")
):
    """Get scan history"""
    return await handle_get_history(limit, agent_code)


@router.get("/deploy-check/")
async def deploy_check():
    """Check if it's safe to deploy now"""
    return await handle_deploy_check()
