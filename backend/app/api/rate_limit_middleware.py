"""DEBT-070: rate limiting in-memory por IP · fixed-window 60s · single-instance.

Cablea settings.rate_limit_per_minute (antes config muerta · cero consumidores). Sin
dependencias externas (slowapi/Redis) · válido para el deploy single-instance actual
(APScheduler corre in-process → no hay multi-instancia hoy). Escalar horizontalmente
requeriría un store compartido (Redis).

Se monta ANTES de CORS en main.py → CORS queda outermost y el 429 lleva headers al browser.
"""
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_WINDOW_S = 60.0
_EXEMPT_PREFIXES = ("/health", "/docs", "/redoc", "/openapi")
_MAX_TRACKED_IPS = 5000  # cota de memoria · sweep de IPs inactivas al superarla


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")  # Railway/proxy → IP real es la primera
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window por IP: >limit_per_minute en 60s → HTTP 429 + Retry-After."""

    def __init__(self, app, limit_per_minute: int) -> None:
        super().__init__(app)
        self._limit = max(1, limit_per_minute)
        self._hits: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path.startswith(_EXEMPT_PREFIXES):
            return await call_next(request)
        now = time.monotonic()
        window_start = now - _WINDOW_S
        ip = _client_ip(request)
        hits = [t for t in self._hits.get(ip, ()) if t > window_start]
        if len(hits) >= self._limit:
            retry = max(1, int(_WINDOW_S - (now - hits[0])) + 1)
            self._hits[ip] = hits
            return JSONResponse(
                status_code=429,
                content={"detail": "rate_limited", "retry_after_s": retry},
                headers={"Retry-After": str(retry)},
            )
        hits.append(now)
        self._hits[ip] = hits
        if len(self._hits) > _MAX_TRACKED_IPS:  # sweep IPs sin hits recientes (cota memoria)
            self._hits = {k: v for k, v in self._hits.items() if v and v[-1] > window_start}
        return await call_next(request)
