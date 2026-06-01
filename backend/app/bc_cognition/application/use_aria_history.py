"""Use case: cargar historial de conversación ARIA del usuario.

DDD A1 + A9: delegación a aria_repository · solo retorna rows brutos.
El handler los empaqueta en ARIAHistoryResponse.
"""
from typing import Any
from app.bc_cognition.infrastructure import aria_repository as repo
from app.infrastructure.supabase_service import get_supabase_service


async def use_aria_history(
    user_id: str, limit: int | None = None, client_id: str | None = None,
) -> list[dict[str, Any]]:
    """Últimos N mensajes ASC del user. limit=None → default del repository. Switcher V1:
    client_id → solo ese negocio (ausente = todo el user, legacy)."""
    supabase = get_supabase_service()
    if limit is None:
        return repo.load_history_for_endpoint(supabase, user_id, client_id=client_id)
    return repo.load_history_for_endpoint(supabase, user_id, limit, client_id=client_id)
