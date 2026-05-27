"""DEBT-052 · servicio de créditos prepagados (check + débito).

Hard block (402) al agotar el budget prepagado del periodo (decisión owner ·
prepago estricto · margen 100%). Solo aplica a clientes ENROLADOS (con fila en
client_agent_credits); clientes sin pack NO se gatean (siguen con su plan · no
se rompe a los existentes). limits_omega.MAX_USD_DIARIO_API_POR_CLIENTE sigue
siendo el circuit-breaker diario INDEPENDIENTE (no se modifica · G1 · pre-existente
sin enforce). Este servicio gatea el budget MENSUAL prepagado. I/O sync en to_thread (DEBT-074).
"""
import logging
import asyncio
from typing import Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_billing.domain.credit_costs import RECHARGE_THRESHOLD

logger = logging.getLogger(__name__)


def _get_row(client_id: str) -> Optional[dict]:
    sb = get_supabase_service().client
    r = (sb.table("client_agent_credits")
         .select("budget_usd_mensual, consumido_usd, packs")
         .eq("client_id", client_id).limit(1).execute())
    return r.data[0] if r.data else None


async def check_budget(client_id: str) -> bool:
    """True si el cliente puede generar. Sin fila (no enrolado) → True (no se
    gatea). Enrolado → consumido_usd < budget_usd_mensual (Hard block al agotar)."""
    row = await asyncio.to_thread(_get_row, client_id)
    if row is None:
        return True
    return float(row.get("consumido_usd") or 0) < float(row.get("budget_usd_mensual") or 0)


def _debit_sync(client_id: str, agent_code: str, cost_usd: float,
                model: Optional[str], execution_id: Optional[str]) -> None:
    sb = get_supabase_service().client
    row = (sb.table("client_agent_credits").select("consumido_usd")
           .eq("client_id", client_id).limit(1).execute())
    if not row.data:
        return  # no enrolado · no se debita
    nuevo = float(row.data[0].get("consumido_usd") or 0) + float(cost_usd)
    sb.table("client_agent_credits").update({"consumido_usd": nuevo}).eq("client_id", client_id).execute()
    sb.table("client_credit_ledger").insert({
        "client_id": client_id, "agent_code": agent_code,
        "cost_usd": cost_usd, "model": model, "execution_id": execution_id,
    }).execute()


async def debit(client_id: str, agent_code: str, cost_usd: float,
                model: Optional[str] = None, execution_id: Optional[str] = None) -> None:
    """Debita cost_usd al cliente enrolado + registra en ledger. Best-effort
    (loguea si falla · no rompe la generación ya completada). Async (to_thread)."""
    if not cost_usd or cost_usd <= 0:
        return
    try:
        await asyncio.to_thread(_debit_sync, client_id, agent_code, cost_usd, model, execution_id)
    except Exception as e:
        logger.error(f"credits.debit failed · client={client_id} agent={agent_code}: {e}")


async def needs_recharge(client_id: str) -> bool:
    """True si saldo ≤ 20% (consumido ≥ 80% budget) · trigger auto-recarga (FASE 4)."""
    row = await asyncio.to_thread(_get_row, client_id)
    budget = float(row.get("budget_usd_mensual") or 0) if row else 0
    return budget > 0 and float(row.get("consumido_usd") or 0) >= RECHARGE_THRESHOLD * budget
