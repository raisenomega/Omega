"""DEBT-052 FASE 4 · cron fin-de-mes · reset de periodos de credit packs.

Filas de client_agent_credits con periodo_end ≤ now → resetea consumido_usd=0 y
abre nuevo periodo (now → +30d). OMEGA RETIENE el saldo no usado (cero rollover ·
decisión owner · prepago estricto · margen): el budget del tier se mantiene (la
suscripción Stripe sigue cobrando), pero lo no consumido NO se acredita al periodo
siguiente. Corre diario (00:05) y procesa lo vencido → robusto a límites de mes.
Best-effort por fila. I/O sync en to_thread (DEBT-074 · no bloquea el event loop).
"""
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_PERIOD_DAYS = 30
_BATCH = 500


def _reset_sync() -> dict:
    sb = get_supabase_service().client
    now = datetime.now(timezone.utc)
    due = (sb.table("client_agent_credits")
           .select("id")
           .lte("periodo_end", now.isoformat()).limit(_BATCH).execute())
    reset = 0
    failed = 0
    for row in (due.data or []):
        try:
            sb.table("client_agent_credits").update({
                "consumido_usd": 0,
                "periodo_start": now.isoformat(),
                "periodo_end": (now + timedelta(days=_PERIOD_DAYS)).isoformat(),
            }).eq("id", row["id"]).execute()
            reset += 1
        except Exception as e:
            failed += 1
            logger.error(f"credit period reset fila {row.get('id')}: {e}")
    return {"reset": reset, "failed": failed}


async def run_credit_period_reset() -> dict:
    """Resetea consumido + abre nuevo periodo de credit packs vencidos. OMEGA retiene saldo."""
    try:
        result = await asyncio.to_thread(_reset_sync)
    except Exception as e:
        logger.error(f"credit_period_reset failed: {e}", exc_info=True)
        return {"reset": 0, "failed": 0, "errors": [str(e)]}
    logger.info(f"credit_period_reset · reset={result['reset']} failed={result['failed']}")
    return result
