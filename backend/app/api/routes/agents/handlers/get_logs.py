"""
Stub handler · DEBT-030: archivo perdido en migración Lovable→V3.
Implementación real pendiente Fase 3 (query supabase agent_logs table).
Ningún endpoint en router.py invoca este handler hoy; solo se importa
para satisfacer agents/handlers/__init__.py.
"""
from fastapi import HTTPException


async def handle_get_logs(agent_id: str):
    """Stub · DEBT-030 · handler no implementado."""
    raise HTTPException(
        status_code=501,
        detail="handle_get_logs not implemented · DEBT-030 · Fase 3"
    )
