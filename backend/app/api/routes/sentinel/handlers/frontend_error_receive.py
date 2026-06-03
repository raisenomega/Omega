"""SENTINEL Capa 9 · receptor PÚBLICO de errores frontend (window.onerror / ErrorBoundary).

Rate limit in-memory por IP (sin slowapi). NO require_superadmin (errores llegan sin login).
Validación de tamaños. Best-effort insert. Nunca expone detalle hacia afuera.
"""
import time
import logging
from typing import Dict, Any
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from pydantic import BaseModel

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_RATE_MAX = 20        # por IP
_RATE_WINDOW = 60     # segundos
_hits: Dict[str, deque] = defaultdict(deque)


class FrontendError(BaseModel):
    message: str
    stack: str = ""
    url: str = ""
    user_agent: str = ""
    signature: str


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "")


def _rate_ok(ip: str, now: float) -> bool:
    dq = _hits[ip]
    while dq and dq[0] < now - _RATE_WINDOW:
        dq.popleft()
    if len(dq) >= _RATE_MAX:
        return False
    dq.append(now)
    return True


async def handle_frontend_error(request: FrontendError, http_request: Request) -> Dict[str, Any]:
    ip = _client_ip(http_request)
    if not _rate_ok(ip, time.time()):
        raise HTTPException(status_code=429, detail="rate limited")
    if len(request.message) > 1000 or len(request.stack) > 5000 or len(request.signature) > 64:
        raise HTTPException(status_code=400, detail="payload too large")
    try:
        get_supabase_service().client.table("frontend_error_log").insert({
            "message": request.message[:1000],
            "stack": request.stack[:5000],
            "url": request.url[:500],
            "signature": request.signature[:64],
            "user_agent": request.user_agent[:500],
            "ip_address": ip,
        }).execute()
    except Exception as e:
        logger.warning(f"frontend_error_log insert skip: {e}")
    return {"received": True}
