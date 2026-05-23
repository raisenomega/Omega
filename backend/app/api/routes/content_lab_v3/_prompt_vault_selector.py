"""Selector del mejor prompt del vault para (vertical, platform, category).

Sprint 1 Subtarea 1.2. Retorna prompt_text con mayor performance_score si existe
matcheo activo · None si no hay match (handler usa fallback default 'Tema: ...').
Spec: CONTENT_LAB_OMEGA_MASTER §15 Sprint 1 ② + §5 (30 prompts seeded).
"""
import logging
from typing import Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def select_optimal_prompt(vertical: str, platform: str, category: str) -> Optional[str]:
    """SELECT prompt con mejor performance_score · None si no match."""
    try:
        sb = get_supabase_service().client
        r = (
            sb.table("prompt_vault")
            .select("prompt_text")
            .eq("vertical", vertical)
            .eq("platform", platform)
            .eq("category", category)
            .eq("is_active", True)
            .order("performance_score", desc=True)
            .limit(1)
            .execute()
        )
        return r.data[0]["prompt_text"] if r.data else None
    except Exception as e:
        logger.error(
            f"vault_selector failed · v={vertical} p={platform} c={category}: {e}"
        )
        return None


class SafeDict(dict):
    """dict que retorna el placeholder visible si la key falta · format_map seguro."""

    def __missing__(self, key: str) -> str:
        return "(no disponible)"
