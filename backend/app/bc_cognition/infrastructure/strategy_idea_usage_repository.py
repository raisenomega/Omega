"""Reads/writes de `strategy_idea_usages` (REDISEÑO Estrategias Fase A · "la idea es la unidad").
service_role · el ownership lo valida el caller (get_strategy_owned) ANTES del insert · aquí el
scope client_id va en el WHERE de los reads/updates. 1 fila por idea usada (UNIQUE strategy_id,idea_idx)."""
from datetime import datetime, timezone
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


def list_idea_usages(supabase: SupabaseService, client_ids: list[str],
                     archived: bool = False) -> list[dict[str, Any]]:
    """Ideas usadas de los clientes accesibles. Scope client_id en el WHERE + embed strategies(titulo)
    (B.1 · 'De: {titulo}'). Fase C.2: archived=False → Usadas (archived_at IS NULL) · True → Archivadas
    (IS NOT NULL). Default false → los consumidores viejos (sin el flag) ven solo las no archivadas."""
    if not client_ids:
        return []
    q = supabase.client.table("strategy_idea_usages").select("*, strategies(titulo)").in_("client_id", client_ids)
    q = q.not_.is_("archived_at", "null") if archived else q.is_("archived_at", "null")
    r = q.order("used_at", desc=True).limit(200).execute()
    return r.data or []


def delete_idea_usage(supabase: SupabaseService, usage_id: str, client_ids: list[str]) -> int:
    """⚠️ HARD DELETE permanente de UNA idea usada (irreversible · Fase C.3). Borra la fila SOLO si es
    del cliente (client_id IN client_ids del servidor en el WHERE) → 0 filas si es ajena (sin fuga ·
    patron DELETE /strategies/{id} · Fase 2). Seguro: strategy_idea_usages no es padre de ningun FK."""
    if not client_ids:
        return 0
    r = supabase.client.table("strategy_idea_usages").delete().eq(
        "id", usage_id).in_("client_id", client_ids).execute()
    return len(r.data or [])


def archive_idea_usage(supabase: SupabaseService, usage_id: str, client_ids: list[str]) -> int:
    """Archiva UNA idea usada (setea archived_at = now → pasa de Usadas a Archivadas). Idempotente
    (re-archivar re-setea). Ownership en el WHERE (client_id IN client_ids del servidor) → 0 filas si
    es ajena (sin fuga). Sin unarchive (una direccion · de Archivadas solo se elimina · decision owner)."""
    if not client_ids:
        return 0
    patch: dict[str, object] = {"archived_at": datetime.now(timezone.utc).isoformat()}
    r = supabase.client.table("strategy_idea_usages").update(patch).eq(
        "id", usage_id).in_("client_id", client_ids).execute()
    return len(r.data or [])
