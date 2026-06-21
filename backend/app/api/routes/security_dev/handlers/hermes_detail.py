"""GET /security-dev/hermes/detail/{integration} · historial + incidentes derivados (HERMES Fase B).

Drill-down de UNA integración: trae TODAS las filas de mcp_health_log de esa integración (no solo el
latest que muestra el panel) y deriva las ventanas de fallo. Modelo (a): cada transición a
'last_use_failed' = un incidente · la recuperación es la fila 'ok'/'no_configurado' siguiente. Sin tabla
nueva, sin migración (el log ya conserva histórico por insert-on-change). Read-only · super_owner.
"""
import logging
from typing import Optional, Dict, Any, List

from app.api.routes.auth.super_owner import require_super_owner
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
_LIMIT = 50  # últimas N transiciones de salud · suficiente para el timeline (insert-on-change = filas raras)


def derive_incidents(rows_desc: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ventanas de fallo desde el historial (PURO · testeable). rows_desc = created_at DESC.
    Cada 'last_use_failed' abre un incidente; la fila 'ok'/'no_configurado' siguiente (cronológica) lo
    cierra. Fallos consecutivos colapsan (refrescan last_failure_at · ver caveat del log)."""
    incidents: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    for row in reversed(rows_desc):  # cronológico: viejo → nuevo
        if row.get("status") == "last_use_failed":
            if cur is None:
                cur = {"started_at": row.get("created_at"), "detail": row.get("detail"),
                       "last_failure_at": row.get("last_use") or row.get("created_at"), "recovered_at": None}
            else:
                cur["last_failure_at"] = row.get("last_use") or row.get("created_at")
        elif cur is not None:  # ok / no_configurado = recuperación → cierra el incidente
            cur["recovered_at"] = row.get("created_at")
            incidents.append(cur)
            cur = None
    if cur is not None:
        incidents.append(cur)  # incidente ABIERTO (aún sin recuperación)
    incidents.reverse()  # más reciente primero (para la UI)
    return incidents


async def handle_hermes_detail(integration: str, authorization: Optional[str]) -> Dict[str, Any]:
    await require_super_owner(authorization)
    try:
        sb = get_supabase_service().client
        r = (sb.table("mcp_health_log")
             .select("status, detail, last_use, checked_at, created_at")
             .eq("integration", integration).order("created_at", desc=True).limit(_LIMIT).execute())
        rows = r.data or []
        return {"integration": integration, "timeline": rows, "incidents": derive_incidents(rows)}
    except Exception as e:
        logger.error(f"handle_hermes_detail failed: {e}", exc_info=True)
        return {"integration": integration, "timeline": [], "incidents": [], "error": str(e)}
