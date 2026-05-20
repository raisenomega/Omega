"""aria_v1 · ARIA endpoints (Fase 1) · /api/v1/aria/{message,history,track}.

Spec: ARIA_NOVA_INTELLIGENCE.md §4-§5. ARIA es proyección de NOVA con
contexto por rol (cliente PYME vs reseller). SIEMPRE captura conversación
en agent_memory + behavioral_events.
"""
from app.api.routes.aria_v1.router import router

__all__ = ["router"]
