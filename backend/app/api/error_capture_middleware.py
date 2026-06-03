"""SENTINEL Capa 9 · middleware de captura de errores backend (5xx + exceptions no manejadas).

INSERT best-effort en backend_error_log · NUNCA bloquea ni rompe el request. Solo escribe en
errores (el success path solo chequea status_code → overhead ~nulo). NO captura body (privacy).
"""
import logging
import traceback
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else ""


def _log_error(request: Request, status_code: int, error_class: str,
               error_message: Optional[str], stack: Optional[str]) -> None:
    try:
        get_supabase_service().client.table("backend_error_log").insert({
            "request_path": str(request.url.path),
            "http_method": request.method,
            "status_code": status_code,
            "error_class": error_class,
            "error_message": (error_message or "")[:2000],
            "stack_trace": (stack or "")[:8000],
            "ip_address": _client_ip(request),
            "user_agent": request.headers.get("user-agent", "")[:500],
        }).execute()
    except Exception as e:
        logger.warning(f"backend_error_log insert skip (best-effort): {e}")


class SentinelErrorCaptureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception as exc:
            _log_error(request, 500, type(exc).__name__, str(exc), traceback.format_exc())
            raise
        if response.status_code >= 500:
            _log_error(request, response.status_code, "HTTPStatus", str(response.status_code), None)
        return response
