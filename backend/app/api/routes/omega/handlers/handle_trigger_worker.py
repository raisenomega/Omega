# backend/app/api/routes/omega/handlers/handle_trigger_worker.py
# MAX 200 LINES — R-LINES-001
# Trigger Worker — dispara workers manualmente para testing

from fastapi import HTTPException


async def handle_trigger_worker(worker_name: str, client_id: str | None = None):
    """
    Dispara un worker manualmente.
    Si client_id se provee → run_for_client
    Si no → run_all_clients

    Lazy import para evitar fallos en tiempo de carga del módulo.
    """
    if worker_name == "news_monitor":
        # Lazy import — solo cuando se ejecuta
        from app.workers.news_monitor_worker import NewsMonitorWorker

        worker = NewsMonitorWorker()
        if client_id:
            await worker.run_for_client(client_id)
            result = {"status": "completed", "worker": worker_name, "client_id": client_id}
        else:
            await worker.run_all_clients()
            result = {"status": "completed", "worker": worker_name, "mode": "all_clients"}
        return result

    elif worker_name == "competitor_tracker":
        # Lazy import — solo cuando se ejecuta
        from app.workers.competitor_tracker_worker import CompetitorTrackerWorker

        worker = CompetitorTrackerWorker()
        if client_id:
            await worker.run_for_client(client_id)
            result = {"status": "completed", "worker": worker_name, "client_id": client_id}
        else:
            await worker.run_all_clients()
            result = {"status": "completed", "worker": worker_name, "mode": "all_clients"}
        return result

    elif worker_name == "trend_spotter":
        # Lazy import — solo cuando se ejecuta
        from app.workers.trend_spotter_worker import TrendSpotterWorker

        worker = TrendSpotterWorker()
        if client_id:
            await worker.run_for_client(client_id)
            result = {"status": "completed", "worker": worker_name, "client_id": client_id}
        else:
            await worker.run_all_clients()
            result = {"status": "completed", "worker": worker_name, "mode": "all_clients"}
        return result

    raise HTTPException(404, f"Worker '{worker_name}' not found")
