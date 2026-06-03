"""SENTINEL Capa 3 · agrega security headers a TODA response del backend (defensa en profundidad).

NO incluye CSP a propósito: /docs (Swagger UI) y /redoc son HTML y una CSP estricta los rompe;
la CSP del producto vive en el frontend (vercel.json · Report-Only). Se monta OUTERMOST en main.py
(último add_middleware) → cubre también respuestas de error de los middlewares internos.
setdefault: no pisa un header ya seteado por un handler específico.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inyecta los headers de seguridad estándar (sin CSP) en cada response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        for k, v in _HEADERS.items():
            response.headers.setdefault(k, v)
        return response
