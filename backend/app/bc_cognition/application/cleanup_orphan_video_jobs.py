"""Cron job: marca jobs orphan (status='running' >15min) como failed.

DEBT-045 Sprint 3 · si Railway reinicia mid-generation o worker crashea (asyncio
cancellation, OOM, network), el row queda en 'running' indefinida (orphan). Este
cron horario detecta y limpia · usuario ve 'failed' en vez de 'Generando…' infinito.

Threshold 15 min = 3x el max típico de Veo (5min poll + 30s download + 30s upload).
False positives extremadamente improbable. Cron interval 1h: balance entre noise
y tiempo visible del orphan al usuario.

Registrado en main.py:on_startup como cron 'interval', hours=1.
"""
import logging
from datetime import datetime, timedelta, timezone

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_ORPHAN_THRESHOLD_MINUTES = 15


async def cleanup_orphan_video_jobs() -> None:
    """Cron horario · marca jobs 'running' >15min como 'failed' (orphan_timeout)."""
    cutoff_iso = (
        datetime.now(timezone.utc) - timedelta(minutes=_ORPHAN_THRESHOLD_MINUTES)
    ).isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        sb = get_supabase_service().client
        r = (
            sb.table("video_generation_jobs").update({
                "status": "failed",
                "error": f"orphan_timeout: worker no completó en {_ORPHAN_THRESHOLD_MINUTES}min · revisar Railway logs",
                "completed_at": now_iso,
            })
            .eq("status", "running").lt("started_at", cutoff_iso).execute()
        )
        n = len(r.data) if r.data else 0
        if n > 0:
            logger.warning(
                f"cleanup_orphan_video_jobs: marcados {n} orphan jobs "
                f"como failed (>{_ORPHAN_THRESHOLD_MINUTES}min en running)"
            )
        else:
            logger.info("cleanup_orphan_video_jobs: cero orphans · sistema sano")
    except Exception as e:
        logger.error(f"cleanup_orphan_video_jobs failed: {e}", exc_info=True)
