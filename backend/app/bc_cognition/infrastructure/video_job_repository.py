"""Repository video_generation_jobs · CRUD para background job pattern.

DEBT-020 Sprint 2 · POST handler insert_pending → worker update_running →
completed/failed · GET handler fetch_job. Pattern función libre síncrona +
singleton _sb() interno. Service role bypasses RLS para todas las escrituras.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb():
    return get_supabase_service().client


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_pending_job(client_id: str, prompt: str, ratio: str) -> str:
    """INSERT con status='pending' · raise si falla · handler captura detail."""
    r = _sb().table("video_generation_jobs").insert({
        "client_id": client_id, "prompt": prompt, "ratio": ratio,
        "status": "pending",
    }).execute()
    if not r.data:
        raise RuntimeError("insert returned no data")
    return str(r.data[0]["id"])


def update_job_running(job_id: str) -> None:
    """Status pending → running · setea started_at."""
    _sb().table("video_generation_jobs").update({
        "status": "running", "started_at": _now_iso(),
    }).eq("id", job_id).execute()


def update_job_completed(job_id: str, video_url: str, metadata: dict) -> None:
    """Status running → completed · setea video_url + metadata + completed_at."""
    _sb().table("video_generation_jobs").update({
        "status": "completed", "video_url": video_url, "metadata": metadata,
        "completed_at": _now_iso(),
    }).eq("id", job_id).execute()


def update_job_failed(job_id: str, error: str) -> None:
    """Status → failed · error truncado a 500 chars + completed_at."""
    _sb().table("video_generation_jobs").update({
        "status": "failed", "error": error[:500], "completed_at": _now_iso(),
    }).eq("id", job_id).execute()


def update_job_cancelled(job_id: str) -> None:
    """DEBT-CL-010: Status → cancelled · completed_at. Idempotente vía
    handler (chequea estado antes de llamar)."""
    _sb().table("video_generation_jobs").update({
        "status": "cancelled", "completed_at": _now_iso(),
    }).eq("id", job_id).execute()


def fetch_job(job_id: str) -> Optional[dict[str, Any]]:
    """Lee fila completa · handler hace ownership check (no leak existence)."""
    try:
        r = _sb().table("video_generation_jobs").select("*").eq("id", job_id).limit(1).execute()
        return r.data[0] if r.data else None
    except Exception as e:
        logger.error(f"fetch_job failed · job_id={job_id}: {e}", exc_info=True)
        return None
