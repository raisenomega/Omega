"""Repository image_generation_jobs · CRUD para background job pattern (DEBT-IMAGE-ASYNC · F1).

Espejo de video_job_repository (00018). POST handler insert_pending → worker update_running →
completed/failed · GET handler fetch_job. Función libre síncrona + singleton _sb() interno.
Service role bypasses RLS para todas las escrituras. NO toca el flujo de video.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_TABLE = "image_generation_jobs"


def _sb():
    return get_supabase_service().client


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def insert_pending_job(client_id: str, prompt: str, size: str, quality: str,
                       metadata: Optional[dict] = None) -> str:
    """INSERT status='pending' · raise si falla · handler captura detail.
    metadata jsonb persiste los params de gen (style/aspect/apply_logo/logo_url/refs)
    para que el worker (F2) los lea tras fetch_job sin recibir el request original."""
    payload: dict = {
        "client_id": client_id, "prompt": prompt, "size": size,
        "quality": quality, "status": "pending",
    }
    if metadata:
        payload["metadata"] = metadata
    r = _sb().table(_TABLE).insert(payload).execute()
    if not r.data:
        raise RuntimeError("insert returned no data")
    return str(r.data[0]["id"])


def update_job_running(job_id: str) -> None:
    """Status pending → running · setea started_at."""
    _sb().table(_TABLE).update({
        "status": "running", "started_at": _now_iso(),
    }).eq("id", job_id).execute()


def update_job_completed(job_id: str, image_url: str, metadata: dict) -> None:
    """Status running → completed · setea image_url + metadata + completed_at."""
    _sb().table(_TABLE).update({
        "status": "completed", "image_url": image_url, "metadata": metadata,
        "completed_at": _now_iso(),
    }).eq("id", job_id).execute()


def update_job_failed(job_id: str, error: str) -> None:
    """Status → failed · error truncado a 500 chars + completed_at."""
    _sb().table(_TABLE).update({
        "status": "failed", "error": error[:500], "completed_at": _now_iso(),
    }).eq("id", job_id).execute()


def update_job_cancelled(job_id: str) -> None:
    """Status → cancelled · completed_at. Idempotente vía handler (chequea estado antes)."""
    _sb().table(_TABLE).update({
        "status": "cancelled", "completed_at": _now_iso(),
    }).eq("id", job_id).execute()


def fetch_job(job_id: str) -> Optional[dict[str, Any]]:
    """Lee fila completa · handler hace ownership check (no leak existence)."""
    try:
        r = _sb().table(_TABLE).select("*").eq("id", job_id).limit(1).execute()
        return r.data[0] if r.data else None
    except Exception as e:
        logger.error(f"fetch_job failed · job_id={job_id}: {e}", exc_info=True)
        return None
