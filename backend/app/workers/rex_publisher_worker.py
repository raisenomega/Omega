# backend/app/workers/rex_publisher_worker.py
# MAX 200 LINES — R-LINES-001
"""REX Publisher Worker (DEBT-098 · F2) · publica autónomo los due posts aprobados.

Cron cada 5 min · subclase BaseWorker (circuit breaker R-WORKER-001 + omega_worker_logs +
semáforo 5). Solo recorre clientes con rex_addon_active AND autonomous_mode_on. La publish_fn
la selecciona el wrapper según REX_LIVE_ENABLED (default OFF=shadow · REX inerte hasta GO).
"""
from __future__ import annotations
import asyncio
import logging

from app.workers.base_worker import BaseWorker
from app.workers.rex_publish_fn import select_publish_fn
from app.bc_cognition.application.rex_publish_uc import run_rex_for_client
from app.bc_cognition.infrastructure import rex_publish_repository as repo

logger = logging.getLogger(__name__)


class RexPublisherWorker(BaseWorker):
    """Publicador autónomo · gate determinístico de 7 checks · publish_fn inyectada."""

    name = "rex_publisher"

    async def _get_active_clients(self) -> list[str]:
        """Override · solo clientes con add-on comprado Y toggle encendido (no todos los activos)."""
        try:
            return await asyncio.to_thread(repo.fetch_active_rex_client_ids)
        except Exception as e:
            logger.error(f"[rex_publisher] error fetching clients: {e}")
            return []

    async def execute(self, client_id: str) -> dict:
        """Delega al use case · publish_fn según REX_LIVE_ENABLED (la decide el wrapper)."""
        return await run_rex_for_client(client_id, select_publish_fn())


rex_publisher_worker = RexPublisherWorker()


async def run_rex_publisher_job() -> None:
    """Entry-point del cron (main.py · cada 5 min · max_instances=1)."""
    await rex_publisher_worker.run_all_clients()
