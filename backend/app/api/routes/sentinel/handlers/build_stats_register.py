"""SENTINEL Capa 10 · receptor de build stats del GitHub Action · auth X-Sentinel-Token."""
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.sentinel.handlers.security_scan_report import _valid_token  # reusa hmac constante-time

logger = logging.getLogger(__name__)


class BuildStats(BaseModel):
    git_sha: str
    bundle_size_kb: int
    main_chunk_kb: Optional[int] = None
    vendor_chunk_kb: Optional[int] = None
    total_chunks: Optional[int] = None
    build_duration_s: Optional[float] = None
    github_run_id: Optional[str] = None


async def handle_build_stats(request: BuildStats, x_sentinel_token: Optional[str]) -> Dict[str, Any]:
    """Persiste stats del build (bundle size + chunks) · auth machine-to-machine."""
    if not _valid_token(x_sentinel_token):
        raise HTTPException(status_code=401, detail="Invalid SENTINEL token")
    supabase = get_supabase_service()
    resp = supabase.client.table("frontend_build_stats").insert({
        "git_sha": request.git_sha,
        "bundle_size_kb": request.bundle_size_kb,
        "main_chunk_kb": request.main_chunk_kb,
        "vendor_chunk_kb": request.vendor_chunk_kb,
        "total_chunks": request.total_chunks,
        "build_duration_s": request.build_duration_s,
        "github_run_id": request.github_run_id,
    }).execute()
    rec_id = (resp.data or [{}])[0].get("id")
    logger.info(f"build stats: {request.git_sha[:8]} {request.bundle_size_kb}kb")
    return {"received": True, "build_record_id": rec_id}
