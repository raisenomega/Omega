"""HERMES alerta inmediata · cron cada 5 min (Fase B+ · nivel 2).

Anti-spam por el mecanismo del log: mcp_health_log inserta UNA fila por TRANSICIÓN (ok→last_use_failed);
fallos repetidos = UPDATE (created_at no cambia). → una sola alerta cuando el incidente ABRE (created_at
dentro de la ventana del cron). Un outage persistente NO re-alerta (su created_at queda viejo). Solo
integraciones CRÍTICAS (zernio/anthropic/stripe). Best-effort: una notificación que falla NO rompe el cron.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, List, Dict, Optional

from app.bc_cognition.infrastructure import hermes_alerts
from app.bc_cognition.application.alert_dispatcher import dispatch_hermes_alert

logger = logging.getLogger(__name__)
_WINDOW_MIN = 6  # ventana ~= intervalo del cron (5 min) + 1 margen · evita re-alertar incidentes viejos


def _parse(at: Optional[str]) -> Optional[datetime]:
    if not at:
        return None
    try:
        return datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    except ValueError:
        return None


def select_alerts(latest_rows: List[Dict[str, Any]], now: datetime) -> List[Dict[str, Any]]:
    """PURO: de las últimas filas por integración crítica, las que ABRIERON incidente recién (status
    last_use_failed Y created_at dentro de la ventana). Anti-spam: un incidente viejo (created_at fuera
    de ventana) NO re-alerta · una integración menor NO entra · una recuperada (status ok) NO alerta."""
    out: List[Dict[str, Any]] = []
    for row in latest_rows:
        if row.get("integration") not in hermes_alerts.HERMES_CRITICAL:
            continue
        if row.get("status") != "last_use_failed":
            continue
        created = _parse(row.get("created_at"))
        if created is None:
            continue
        if (now - created).total_seconds() / 60 <= _WINDOW_MIN:
            out.append(row)
    return out


async def run_hermes_alert_check() -> Dict[str, int]:
    """Cron 5 min: alerta inmediata por integración crítica recién caída (1 por incidente · best-effort)."""
    try:
        rows = await asyncio.to_thread(hermes_alerts.latest_critical)
    except Exception as e:
        logger.error(f"hermes_alert_check · lectura falló: {e}", exc_info=True)
        return {"checked": 0, "alerted": 0}
    to_alert = select_alerts(rows, datetime.now(timezone.utc))
    sent = 0
    for row in to_alert:
        try:  # una notificación que falla NO rompe el cron ni las demás
            if await dispatch_hermes_alert(str(row.get("integration")), str(row.get("detail") or "")):
                sent += 1
        except Exception as e:
            logger.error(f"hermes_alert_check · dispatch {row.get('integration')} falló: {e}", exc_info=True)
    if to_alert:
        logger.info(f"hermes_alert_check · críticas caídas={len(to_alert)} alertas_enviadas={sent}")
    return {"checked": len(rows), "alerted": sent}
