"""DEBT-052 FASE 4 · operaciones superadmin sobre créditos (mover/liberar).

Solo superadmin (gateado en el handler con require_superadmin). Escrituras async
(to_thread · DEBT-074). Cada movimiento deja fila de auditoría en client_credit_ledger
con agent_code "__admin_*" (la AI Tab de FASE 5 filtra estos del consumo por agente).

- transfer_credits: mueve budget mensual de un cliente a otro (no puede dejar el
  budget origen por debajo de lo ya consumido · ambos deben estar enrolados).
- release_credits: libera consumo de un cliente (reduce consumido_usd · grace admin
  · sin cobro nuevo · floor 0).

CAVEAT V1 (no atómico): transfer hace 2 updates sin transacción (Supabase REST). Op
superadmin rara y recuperable manualmente · atomicidad vía RPC = follow-up (ver SOT).
"""
import logging
import asyncio
from typing import Optional
from app.bc_billing.domain.billing_events import BillingResult, ok, fail
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _row(sb, client_id: str) -> Optional[dict]:
    r = (sb.table("client_agent_credits")
         .select("budget_usd_mensual, consumido_usd")
         .eq("client_id", client_id).limit(1).execute())
    return r.data[0] if r.data else None


def _ledger(sb, client_id: str, agent_code: str, amount: float, note: str) -> None:
    sb.table("client_credit_ledger").insert({
        "client_id": client_id, "agent_code": agent_code,
        "cost_usd": amount, "model": note,
    }).execute()


def _transfer_sync(from_client: str, to_client: str, amount: float) -> BillingResult:
    sb = get_supabase_service().client
    src, dst = _row(sb, from_client), _row(sb, to_client)
    if src is None or dst is None:
        return fail("Ambos clientes deben estar enrolados (con credit pack)", "not_enrolled")
    src_budget = float(src.get("budget_usd_mensual") or 0)
    if src_budget - amount < float(src.get("consumido_usd") or 0):
        return fail("El budget origen no puede quedar por debajo de lo ya consumido", "insufficient_budget")
    sb.table("client_agent_credits").update(
        {"budget_usd_mensual": float(dst.get("budget_usd_mensual") or 0) + amount}).eq("client_id", to_client).execute()
    sb.table("client_agent_credits").update(
        {"budget_usd_mensual": src_budget - amount}).eq("client_id", from_client).execute()
    _ledger(sb, from_client, "__admin_transfer_out__", amount, f"to:{to_client}")
    _ledger(sb, to_client, "__admin_transfer_in__", amount, f"from:{from_client}")
    return ok({"from_client": from_client, "to_client": to_client, "amount_usd": amount})


def _release_sync(client_id: str, amount: float) -> BillingResult:
    sb = get_supabase_service().client
    row = _row(sb, client_id)
    if row is None:
        return fail("Cliente no enrolado (sin credit pack)", "not_enrolled")
    nuevo = max(0.0, float(row.get("consumido_usd") or 0) - amount)
    sb.table("client_agent_credits").update(
        {"consumido_usd": nuevo}).eq("client_id", client_id).execute()
    _ledger(sb, client_id, "__admin_release__", amount, "release")
    return ok({"client_id": client_id, "consumido_usd": nuevo})


async def transfer_credits(from_client: str, to_client: str, amount_usd: float) -> BillingResult:
    """Mueve budget mensual de un cliente a otro (superadmin)."""
    if amount_usd <= 0:
        return fail("El monto debe ser > 0", "invalid_amount")
    if from_client == to_client:
        return fail("Origen y destino no pueden ser el mismo cliente", "same_client")
    try:
        return await asyncio.to_thread(_transfer_sync, from_client, to_client, amount_usd)
    except Exception as e:
        logger.error(f"transfer_credits failed: {e}", exc_info=True)
        return fail(f"Error de infraestructura: {e}", "infra_error")


async def release_credits(client_id: str, amount_usd: float) -> BillingResult:
    """Libera consumo de un cliente (reduce consumido · grace admin · floor 0)."""
    if amount_usd <= 0:
        return fail("El monto debe ser > 0", "invalid_amount")
    try:
        return await asyncio.to_thread(_release_sync, client_id, amount_usd)
    except Exception as e:
        logger.error(f"release_credits failed: {e}", exc_info=True)
        return fail(f"Error de infraestructura: {e}", "infra_error")
