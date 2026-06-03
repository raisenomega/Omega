"""SENTINEL Capa 5 — monitoreo de rotación de secrets (cron mensual · log-only V1).

Lista CERRADA (solo críticos · NO os.environ dinámico). Nunca toca el valor del secret,
solo su nombre + el timestamp de la última rotación registrada manualmente por el owner.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# Política de rotación en días (alineada con la criticidad de cada secret).
SECRETS_ROTATION_POLICY: Dict[str, int] = {
    "ANTHROPIC_API_KEY": 90,
    "SUPABASE_SERVICE_ROLE_KEY": 90,
    "STRIPE_SECRET_KEY": 90,
    "STRIPE_WEBHOOK_SECRET": 90,
    "GOOGLE_CLIENT_SECRET": 90,
    "SENTINEL_TOKEN": 90,
    "SUPABASE_JWT_SECRET": 180,    # cambio invalida sesiones → ventana más larga
    "TOKEN_ENCRYPTION_KEY": 180,
    "BRAVE_API_KEY": 90,
    "RESEND_API_KEY": 90,
}
WARN_LEAD_DAYS = 5


def _latest_rotations() -> Dict[str, Dict[str, Any]]:
    """Última fila por secret_name (rotated_at desc). {name: row}."""
    sb = get_supabase_service().client
    resp = sb.table("sentinel_secrets_log")\
        .select("secret_name,rotated_at,note")\
        .order("rotated_at", desc=True).execute()
    latest: Dict[str, Dict[str, Any]] = {}
    for r in (resp.data or []):
        latest.setdefault(r["secret_name"], r)
    return latest


def compute_rotation_status() -> List[Dict[str, Any]]:
    """Estado completo por secret (incluye 'ok') · baseline_unknown si nunca se rotó."""
    latest = _latest_rotations()
    now = datetime.now(timezone.utc)
    out: List[Dict[str, Any]] = []
    for name, max_days in SECRETS_ROTATION_POLICY.items():
        row = latest.get(name)
        rotated_at: Optional[str] = row.get("rotated_at") if row else None
        if not rotated_at:
            urgency, days = "baseline_unknown", None
        else:
            days = (now - datetime.fromisoformat(rotated_at)).days
            urgency = "urgent" if days >= max_days else "warn" if days >= max_days - WARN_LEAD_DAYS else "ok"
        out.append({
            "secret_name": name, "last_rotated_at": rotated_at, "days_since": days,
            "max_days": max_days, "urgency": urgency, "note": row.get("note") if row else None,
        })
    return out


def check_secrets_rotation() -> List[Dict[str, Any]]:
    """Solo los que NO están 'ok' (warn/urgent/baseline_unknown)."""
    return [s for s in compute_rotation_status() if s["urgency"] != "ok"]


async def run_secrets_rotation_check() -> Dict[str, Any]:
    """Cron mensual (primer lunes 3am AST) · log-only · NO inserta filas (rotación = acción manual)."""
    alerts = check_secrets_rotation()
    urgent = [a for a in alerts if a["urgency"] == "urgent"]
    if urgent:
        logger.warning(f"SENTINEL secrets: {len(urgent)} rotaciones URGENTES: {[a['secret_name'] for a in urgent]}")
    else:
        logger.info(f"SENTINEL secrets: {len(alerts)} alerts (0 urgentes)")
    return {"alerts": alerts, "urgent_count": len(urgent)}
