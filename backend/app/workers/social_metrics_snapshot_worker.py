"""Cron diario (6am AST = 10:00 UTC · el scheduler corre en AST) · snapshot de social_metrics (Arco 1 · Fase 2 · solo ESCRITURA).

Por negocio activo: list_accounts (followers por red) + daily-metrics (actividad per-día) → builder
honesto → upsert idempotente. BEST-EFFORT por negocio: un fallo de Zernio de uno NO tumba la corrida
ni escribe basura (ese negocio queda sin fila ese día · hueco honesto). Cierra el gap "Zernio no tiene
ventana" → histórico propio para "últimos 90 días" y el was_correct de LUAN (futuro · acá solo se puebla).
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from app.bc_cognition.infrastructure import social_metrics_repository as repo
from app.bc_cognition.infrastructure import zernio_analytics_adapter as za
from app.workers._social_metrics_builder import build_snapshot_rows

logger = logging.getLogger(__name__)


def _now() -> datetime:
    """Punto de inyección (tests deterministas · lección DEBT-HERMES-CRON-TEST-TIME)."""
    return datetime.now(timezone.utc)


async def run(today: Optional[str] = None) -> dict:
    """Corre el snapshot. today (ISO date) inyectable para tests · default = hoy UTC."""
    day = today or _now().date().isoformat()
    profiles = await asyncio.to_thread(repo.fetch_active_profiles)
    if not profiles:
        return {"profiles": 0, "rows": 0}
    try:
        accounts = await za.list_accounts()   # todas del workspace · el builder filtra por profile_id
    except Exception as e:
        logger.error(f"social_metrics snapshot: list_accounts falló: {e}")
        accounts = []
    total = 0
    for p in profiles:
        try:
            daily = await za.daily_metrics(p["profile_id"])
            rows = build_snapshot_rows(daily, accounts, p["client_id"], p["profile_id"], day)
            total += await asyncio.to_thread(repo.upsert_social_metrics, rows)
        except Exception as e:   # best-effort: este negocio queda sin fila (hueco honesto), sigue el resto
            logger.warning(f"social_metrics snapshot: client={p['client_id']} falló (best-effort): {e}")
    logger.info(f"social_metrics snapshot: {total} filas · {len(profiles)} negocios · {day}")
    return {"profiles": len(profiles), "rows": total}
