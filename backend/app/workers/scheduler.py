# backend/app/workers/scheduler.py
# MAX 200 LINES — R-LINES-001
# OMEGA Scheduler — activa workers autónomos 24/7
# Se inicia con FastAPI en startup

from __future__ import annotations
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.workers.news_monitor_worker import NewsMonitorWorker
from app.workers.competitor_tracker_worker import CompetitorTrackerWorker
from app.workers.trend_spotter_worker import TrendSpotterWorker

logger = logging.getLogger(__name__)

# Instancia global del scheduler
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="America/Puerto_Rico")
    return _scheduler


def setup_workers(scheduler: AsyncIOScheduler) -> None:
    """Registra todos los workers con sus frecuencias."""

    news_worker = NewsMonitorWorker()

    # ── NEWS MONITOR — cada 2 horas ──────────────────────────────────────────
    scheduler.add_job(
        func        = news_worker.run_all_clients,
        trigger     = IntervalTrigger(hours=2),
        id          = "news_monitor",
        name        = "News Monitor — noticias por industria",
        replace_existing = True,
        max_instances    = 1,  # nunca dos corriendo al mismo tiempo
    )

    # ── COMPETITOR TRACKER — cada 6 horas ────────────────────────────────────
    competitor_tracker = CompetitorTrackerWorker()
    scheduler.add_job(
        func        = competitor_tracker.run_all_clients,
        trigger     = IntervalTrigger(hours=6),
        id          = "competitor_tracker",
        name        = "Competitor Tracker — monitorea competidores",
        replace_existing = True,
        max_instances    = 1,
    )

    # ── TREND SPOTTER — cada 12 horas ────────────────────────────────────────
    trend_spotter = TrendSpotterWorker()
    scheduler.add_job(
        func        = trend_spotter.run_all_clients,
        trigger     = IntervalTrigger(hours=12),
        id          = "trend_spotter",
        name        = "Trend Spotter — detecta tendencias cada 12h",
        replace_existing = True,
        max_instances    = 1,
    )

    # ── SENTINEL SCAN — diario 3am ───────────────────────────────────────────
    # scheduler.add_job(
    #     func    = SentinelWorker().run_all_clients,
    #     trigger = CronTrigger(hour=3, minute=0),
    #     id      = "sentinel_scan",
    #     replace_existing = True,
    #     max_instances    = 1,
    # )

    # ── COMPETITOR TRACKER — diario 6am ─────────────────────────────────────
    # scheduler.add_job(
    #     func    = CompetitorTrackerWorker().run_all_clients,
    #     trigger = CronTrigger(hour=6, minute=0),
    #     id      = "competitor_tracker",
    #     replace_existing = True,
    #     max_instances    = 1,
    # )

    # ── TREND SPOTTER — cada 4 horas ─────────────────────────────────────────
    # scheduler.add_job(
    #     func    = TrendSpotterWorker().run_all_clients,
    #     trigger = IntervalTrigger(hours=4),
    #     id      = "trend_spotter",
    #     replace_existing = True,
    #     max_instances    = 1,
    # )

    logger.info(f"[Scheduler] {len(scheduler.get_jobs())} workers registrados")
    for job in scheduler.get_jobs():
        logger.info(f"  ▸ {job.id} → next run: {job.next_run_time}")


def start_scheduler() -> AsyncIOScheduler:
    """Inicia el scheduler. Llamar en FastAPI startup."""
    scheduler = get_scheduler()
    if scheduler.running:
        logger.info("[Scheduler] Ya estaba corriendo")
        return scheduler
    setup_workers(scheduler)
    scheduler.start()
    logger.info("[Scheduler] ✅ OMEGA Scheduler iniciado — workers activos")
    return scheduler


def stop_scheduler() -> None:
    """Detiene el scheduler. Llamar en FastAPI shutdown."""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Detenido")


def get_worker_status() -> list[dict]:
    """Retorna estado de todos los workers registrados."""
    scheduler = get_scheduler()
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id":            job.id,
            "name":          job.name,
            "next_run":      str(job.next_run_time) if job.next_run_time else None,
            "running":       scheduler.running,
        })
    return jobs
