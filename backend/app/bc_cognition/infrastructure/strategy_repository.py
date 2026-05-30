"""Reads/writes de `strategies` · service_role · DDD A9. El best-effort (safe_insert) lo
envuelve el caller (use case)."""
from datetime import datetime, timezone
from typing import Any, Optional
from app.infrastructure.supabase_service import SupabaseService


def insert_strategy(supabase: SupabaseService, client_id: str, titulo: str,
                    contenido: dict[str, Any], tipo: str) -> Optional[str]:
    """Inserta una estrategia activa · devuelve su id (None si no se creó)."""
    r = supabase.client.table("strategies").insert({
        "client_id": client_id, "titulo": titulo, "contenido": contenido,
        "tipo": tipo, "estado": "active", "created_by_aria": True,
    }).execute()
    return str(r.data[0]["id"]) if r.data else None


def list_strategies(supabase: SupabaseService, client_ids: list[str], estado: str) -> list[dict[str, Any]]:
    """Estrategias de los clientes accesibles, por estado (active = vista · archived = historial)."""
    if not client_ids:
        return []
    r = supabase.client.table("strategies").select("*").in_("client_id", client_ids).eq(
        "estado", estado).order("created_at", desc=True).limit(50).execute()
    return r.data or []


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
