"""Use case: cargar historial de conversación ARIA del usuario.

DDD A1 + A9: delegación a aria_repository · solo retorna rows brutos.
El handler los empaqueta en ARIAHistoryResponse.
"""
from typing import Any
from app.bc_cognition.infrastructure import aria_repository as repo
from app.infrastructure.supabase_service import get_supabase_service


async def use_aria_history(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Retorna últimos N mensajes ASC del usuario para el endpoint GET /history."""
    supabase = get_supabase_service()
    return repo.load_history_for_endpoint(supabase, user_id, limit)
