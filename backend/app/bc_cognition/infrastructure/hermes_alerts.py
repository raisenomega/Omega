"""HERMES notificación · lecturas de mcp_health_log para los 2 niveles (Fase B+ · sin tabla nueva).

failures_last_24h → resumen diario (cuántas ventanas de fallo por integración en 24h).
latest_critical   → alerta inmediata (última fila por integración CRÍTICA · el worker decide).
Best-effort: ante fallo devuelven vacío (la notificación nunca rompe nada · es observabilidad).
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, List, Dict

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# Integraciones cuyo fallo NO puede esperar al resumen diario (publicación que el cliente ve · el
# cerebro LLM · pagos). El resto = solo resumen diario (degradación menor). resend queda fuera del
# inmediato a propósito: es el canal de email (alertar del canal por el canal sería circular).
HERMES_CRITICAL = frozenset({"zernio", "anthropic", "stripe"})


def _sb() -> Any:
    return get_supabase_service().client


def failures_last_24h() -> List[Dict[str, Any]]:
    """Ventanas de fallo (filas last_use_failed = transiciones) por integración en las últimas 24h."""
    start = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    try:
        r = (_sb().table("mcp_health_log").select("integration, created_at")
             .eq("status", "last_use_failed").gte("created_at", start).execute())
    except Exception as e:
        logger.error(f"hermes_alerts.failures_last_24h failed: {e}", exc_info=True)
        return []
    counts: Dict[str, int] = {}
    for row in (r.data or []):
        integ = str(row.get("integration") or "")
        counts[integ] = counts.get(integ, 0) + 1
    return [{"integration": k, "windows": v} for k, v in sorted(counts.items())]


def latest_critical() -> List[Dict[str, Any]]:
    """Última fila (status/detail/created_at) por cada integración CRÍTICA · para la alerta inmediata."""
    out: List[Dict[str, Any]] = []
    for integ in sorted(HERMES_CRITICAL):
        try:
            r = (_sb().table("mcp_health_log").select("integration, status, detail, created_at")
                 .eq("integration", integ).order("created_at", desc=True).limit(1).execute())
            if r.data:
                out.append(r.data[0])
        except Exception as e:
            logger.error(f"hermes_alerts.latest_critical {integ} failed: {e}", exc_info=True)
    return out
