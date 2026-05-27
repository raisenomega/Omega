"""publishing · Auto-publicación real (Publicador agent · RONDA D follow-up).

POST /api/v1/publish/auto · publica un scheduled_post YA aprobado/programado
(status='pending') de verdad vía el token Meta del cliente (OAuth RONDA D).

SAFETY (P2/P3/P4): NUNCA genera ni aprueba contenido. Solo EJECUTA la publicación
real de algo que el humano ya aprobó (status='pending'). Cero fabricación: sin
token Meta → 409 honesto 'meta_not_connected'; status no publicable → 409 honesto.
"""
from app.api.routes.publishing.router import router

__all__ = ["router"]
