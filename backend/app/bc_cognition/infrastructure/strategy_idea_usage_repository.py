"""Reads/writes de `strategy_idea_usages` (REDISEÑO Estrategias Fase A · "la idea es la unidad").
service_role · el ownership lo valida el caller (get_strategy_owned) ANTES del insert · aquí el
scope client_id va en el WHERE de los reads. 1 fila por idea usada (UNIQUE strategy_id,idea_idx)."""
from typing import Any, Optional
from app.infrastructure.supabase_service import SupabaseService


def record_idea_use(supabase: SupabaseService, strategy_id: str, client_id: str,
                    idea_idx: int, platform: Optional[str], brief: Optional[str]) -> None:
    """Registra el uso de UNA idea. Idempotente: upsert on_conflict(strategy_id,idea_idx)
    ignore_duplicates → re-usar la misma idea NO duplica (UNIQUE 00082 respalda). client_id = el real
    de la estrategia (ya validado dueño por get_strategy_owned · ownership upstream)."""
    supabase.client.table("strategy_idea_usages").upsert({
        "strategy_id": strategy_id, "client_id": client_id,
        "idea_idx": idea_idx, "platform": platform, "brief": brief,
    }, on_conflict="strategy_id,idea_idx", ignore_duplicates=True).execute()


def count_idea_usages(supabase: SupabaseService, strategy_id: str) -> int:
    """Nº de ideas distintas usadas de una estrategia (para el flip a 'used' cuando == total)."""
    r = supabase.client.table("strategy_idea_usages").select("idea_idx").eq(
        "strategy_id", strategy_id).execute()
    return len(r.data or [])


def list_idea_usages(supabase: SupabaseService, client_ids: list[str]) -> list[dict[str, Any]]:
    """Ideas usadas de los clientes accesibles (Fase B · vista Usadas). Scope client_id en el WHERE.
    Embed strategies(titulo): PostgREST resuelve el FK strategy_id→strategies y anida el titulo de
    origen ('De: {titulo}') · funciona en cualquier estado de la estrategia · null defensivo si falta."""
    if not client_ids:
        return []
    r = supabase.client.table("strategy_idea_usages").select("*, strategies(titulo)").in_(
        "client_id", client_ids).order("used_at", desc=True).limit(200).execute()
    return r.data or []
