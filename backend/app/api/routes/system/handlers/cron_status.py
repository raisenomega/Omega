"""GET /system/cron-status (P1-5) · compara los jobs activos del scheduler contra
cron_registry (fuente única) · healthy = no falta ninguno. Lazy import del
scheduler global (patrón use_video_job · evita circular en import-time)."""
from typing import Any

from app.workers.cron_registry import CRON_JOB_IDS, EXPECTED_CRON_JOBS


def handle_cron_status() -> dict[str, Any]:
    from app.main import scheduler  # lazy · main ya está cargado cuando se invoca
    jobs = scheduler.get_jobs()
    active = {j.id for j in jobs}
    missing = sorted(CRON_JOB_IDS - active)
    jobs_out = sorted(
        ({"id": j.id,
          "next_run": str(j.next_run_time) if getattr(j, "next_run_time", None) else None}
         for j in jobs),
        key=lambda x: x["id"],
    )
    return {
        "expected": EXPECTED_CRON_JOBS,
        "active": len(jobs),
        "healthy": not missing,
        "missing": missing,
        "unexpected": sorted(active - CRON_JOB_IDS),
        "jobs": jobs_out,
    }
