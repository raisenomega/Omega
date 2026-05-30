"""strategies_v1 · DEBT-096 Fase 1 · Página Estrategias.

POST  /api/v1/strategies/generate       · genera una estrategia on-demand (reusa pipeline ARIA)
GET   /api/v1/strategies/?estado=active  · lista del usuario (active / archived)
PATCH /api/v1/strategies/{id}/status     · archivar / marcar usada
"""
from app.api.routes.strategies_v1.router import router

__all__ = ["router"]
