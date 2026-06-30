"""Reads/writes de `strategies` · service_role · DDD A9. El best-effort (safe_insert) lo
envuelve el caller (use case)."""
from datetime import datetime, timezone
from typing import Any, Optional
from app.infrastructure.supabase_service import SupabaseService


def insert_strategy(supabase: SupabaseService, client_id: str, titulo: str,
                    contenido: dict[str, Any], tipo: str,
                    generation_key: Optional[str] = None) -> Optional[str]:
    """Inserta una estrategia activa · devuelve su id (None si no se creó).
    Con generation_key (cron Fase 2) → upsert idempotente: si la key ya existe (otra corrida
    ganó la carrera) el UNIQUE parcial la ignora y devuelve None. Sin key (manual) → insert normal."""
    row: dict[str, Any] = {
        "client_id": client_id, "titulo": titulo, "contenido": contenido,
        "tipo": tipo, "estado": "active", "created_by_aria": True,
    }
    if generation_key is None:
        r = supabase.client.table("strategies").insert(row).execute()
    else:
        row["generation_key"] = generation_key
        r = supabase.client.table("strategies").upsert(
            row, on_conflict="generation_key", ignore_duplicates=True).execute()
    return str(r.data[0]["id"]) if r.data else None


def list_strategies(supabase: SupabaseService, client_ids: list[str], estado: str) -> list[dict[str, Any]]:
    """Estrategias de los clientes accesibles, por estado (active = vista · archived = historial)."""
    if not client_ids:
        return []
    r = supabase.client.table("strategies").select("*").in_("client_id", client_ids).eq(
        "estado", estado).order("created_at", desc=True).limit(50).execute()
    return r.data or []


def record_use(supabase: SupabaseService, strategy_id: str, last_used: dict[str, str],
               mark_used: bool, client_ids: list[str]) -> int:
    """Registra el ultimo uso (CAPA 1): SET last_used (+ estado='used'/used_at si mark_used). Scopeado
    a client_ids (ownership en el WHERE) → 0 filas si no es del usuario. last_used se sobreescribe."""
    if not client_ids:
        return 0
    patch: dict[str, object] = {"last_used": last_used}
    if mark_used:
        patch["estado"] = "used"
        patch["used_at"] = datetime.now(timezone.utc).isoformat()
    r = supabase.client.table("strategies").update(patch).eq(
        "id", strategy_id).in_("client_id", client_ids).execute()
    return len(r.data or [])


def delete_strategy(supabase: SupabaseService, strategy_id: str, client_ids: list[str]) -> int:
    """⚠️ HARD DELETE permanente (irreversible). Borra la fila SOLO si pertenece a client_ids
    (ownership en el WHERE · client_ids del servidor · NUNCA del input) → 0 filas si es ajena (sin
    fuga · patron update_status). Seguro: ningun FK referencia strategies como padre (no huerfanos)."""
    if not client_ids:
        return 0
    r = supabase.client.table("strategies").delete().eq(
        "id", strategy_id).in_("client_id", client_ids).execute()
    return len(r.data or [])


def update_strategy_status(supabase: SupabaseService, strategy_id: str, estado: str,
                           client_ids: list[str]) -> int:
    """Cambia estado + sella timestamp (used_at/archived_at). Scopeado a client_ids (ownership en el
    WHERE · service_role bypassa RLS) → 0 filas si la estrategia no es del usuario. Devuelve nº filas."""
    if not client_ids:
        return 0
    patch: dict[str, Any] = {"estado": estado}
    now = datetime.now(timezone.utc).isoformat()
    if estado == "archived":
        patch["archived_at"] = now
    elif estado == "used":
        patch["used_at"] = now
    r = supabase.client.table("strategies").update(patch).eq(
        "id", strategy_id).in_("client_id", client_ids).execute()
    return len(r.data or [])
