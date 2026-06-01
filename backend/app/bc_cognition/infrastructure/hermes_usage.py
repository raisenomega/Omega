"""HERMES fase 1.5 · usage-tracking: registra éxito/fallo del USO REAL de una integración.

Complementa hermes_checks (que solo sabe 'configurada?'). Acá un adapter reporta, en cada uso,
si la llamada externa funcionó → HERMES detecta una integración configurada pero CAÍDA.

Estrategia barata (insert-on-change): la tabla mcp_health_log crece con TRANSICIONES de salud
(raras), no con usos (millones). Si el estado se mantiene → UPDATE last_use de la fila más reciente.
Si cambia (ok↔last_use_failed) → INSERT fila nueva (= historial de incidentes legible · futuro tab).

Best-effort ABSOLUTO: es observabilidad, no camino crítico. Fire-and-forget (no agrega latencia al
adapter) · cualquier error se traga · NUNCA rompe la generación/búsqueda que lo invoca."""
import asyncio
import logging
from datetime import datetime, timezone
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _apply_usage(sb, integration: str, ok: bool, detail: str | None) -> str:
    """Núcleo síncrono testeable: decide INSERT (cambio de estado) vs UPDATE (mismo estado).
    Retorna 'insert' | 'update' (para tests). Asume sb = supabase client."""
    target = "ok" if ok else "last_use_failed"
    now = datetime.now(timezone.utc).isoformat()
    last = sb.table("mcp_health_log").select("id,status").eq(
        "integration", integration).order("checked_at", desc=True).limit(1).execute()
    prev = last.data[0] if last.data else None
    if prev and prev.get("status") == target:
        # mismo estado → solo refrescar last_use (no multiplicar filas)
        sb.table("mcp_health_log").update({"last_use": now, "checked_at": now}).eq("id", prev["id"]).execute()
        return "update"
    # transición (o primera vez) → fila nueva
    sb.table("mcp_health_log").insert({
        "integration": integration, "status": target,
        "detail": detail, "last_use": now,
    }).execute()
    return "insert"


async def _record_async(integration: str, ok: bool, detail: str | None) -> None:
    try:
        sb = get_supabase_service().client
        await asyncio.to_thread(_apply_usage, sb, integration, ok, detail)
    except Exception as e:  # observabilidad · nunca propaga al adapter
        logger.warning(f"hermes_usage · record {integration} skip (best-effort): {e}")


def record_mcp_use(integration: str, ok: bool, detail: str | None = None) -> None:
    """Fire-and-forget desde un adapter (sync · no bloquea · no agrega latencia).
    Agenda el registro en el event loop; si no hay loop activo, lo corre best-effort."""
    try:
        asyncio.get_running_loop().create_task(_record_async(integration, ok, detail))
    except RuntimeError:  # sin loop corriendo (contexto sync/test) → ignora silencioso
        pass
