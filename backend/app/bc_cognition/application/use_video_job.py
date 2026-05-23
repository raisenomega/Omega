"""Use case · video background job orchestration · DEBT-020 Sprint 2.

POST handler llama create_video_job() · inserta row pending + APScheduler 'date'
trigger inmediato. Worker _run_video_job ejecuta start+poll+download+upload del
_video_compat. GET handler llama get_video_job() · ownership check en handler.

CRITICAL: _run_video_job envuelve TODO en try/except Exception. Si una
excepción escapa, el row queda en 'running' indefinido (orphan). Doble try:
si update_failed también falla, log explícito visible para debug + ORPHAN tag.

Limitaciones V1 (DEBT futura · documentar en SOURCE_OF_TRUTH al cierre):
  · Memory jobstore APScheduler · jobs perdidos en Railway restart
  · Sin cron cleanup de orphans (rows 'running' sin worker activo)
  · Sin rate limit · futuro max 3 pending por cliente
"""
import logging
from datetime import datetime
from typing import Any, Optional

from app.bc_cognition.infrastructure import video_job_repository as repo
from app.bc_cognition.infrastructure._video_compat import generate_video_compat

logger = logging.getLogger(__name__)


async def create_video_job(client_id: str, prompt: str, ratio: str) -> str:
    """Crea row pending + spawn worker async · retorna job_id inmediato (~50ms).

    Raise (no silencia) si insert falla · handler captura y devuelve detail
    específico al frontend (FIX 4 · observability mejorada)."""
    job_id = repo.insert_pending_job(client_id, prompt, ratio)
    from app.main import scheduler  # lazy · evita circular import
    scheduler.add_job(
        _run_video_job, "date", run_date=datetime.now(),
        args=[job_id], id=f"vjob_{job_id}",
    )
    return job_id


async def _run_video_job(job_id: str) -> None:
    """Background worker · NUNCA permite excepciones escapar (orphan en running)."""
    try:
        job = repo.fetch_job(job_id)
        if not job:
            logger.error(f"_run_video_job: job_id={job_id} not found in DB")
            return
        repo.update_job_running(job_id)
        result = await generate_video_compat(
            prompt=job["prompt"], ratio=job["ratio"],
            client_id=str(job["client_id"]),
        )
        if result.get("status") == "completed":
            repo.update_job_completed(
                job_id, str(result["video_url"]),
                {"model": result.get("model"), "duration": result.get("duration"),
                 "task_id": result.get("task_id"), "ratio": result.get("ratio")},
            )
        else:
            repo.update_job_failed(job_id, str(result.get("error", "unknown")))
    except Exception as e:
        logger.exception(f"_run_video_job uncaught · job_id={job_id}")
        try:
            repo.update_job_failed(
                job_id, f"uncaught: {type(e).__name__}: {str(e)[:400]}",
            )
        except Exception:
            logger.error(
                f"_run_video_job: ALSO failed update_failed · job_id={job_id} · ORPHAN"
            )


def get_video_job(job_id: str) -> Optional[dict[str, Any]]:
    """Lee state · handler hace ownership check vs client_id propio."""
    return repo.fetch_job(job_id)
