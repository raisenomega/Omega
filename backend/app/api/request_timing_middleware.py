"""SENTINEL Capa 10 · middleware de timing por request → request_timing_log.

Fire-and-forget en thread (asyncio.create_task + to_thread) → CERO latencia añadida al hot path.
Mide TODO request salvo paths de infra (health/docs/static). NO captura body/headers (privacy).
"""
import asyncio
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_SKIP_PREFIXES = ("/health", "/docs", "/openapi.json", "/redoc", "/metrics", "/static", "/favicon")


def _insert_sync(path: str, method: str, status: int, duration_ms: int) -> None:
    try:
        get_supabase_service().client.table("request_timing_log").insert({
            "path": path, "method": method, "status_code": status, "duration_ms": duration_ms,
        }).execute()
    except Exception:
        pass  # telemetría best-effort · nunca propaga


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            path = request.url.path
            if not path.startswith(_SKIP_PREFIXES):
                dur = int((time.perf_counter() - start) * 1000)
                try:
                    asyncio.create_task(asyncio.to_thread(_insert_sync, path, request.method, status, dur))
                except Exception:
                    pass
