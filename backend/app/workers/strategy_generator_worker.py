# backend/app/workers/strategy_generator_worker.py
# MAX 200 LINES — R-LINES-001
# StrategyGeneratorWorker — estrategias automáticas por cadencia (DEBT-096 Fase 2).
# Gates REALES del cron: cadence + idempotencia (generation_key UNIQUE) + budget.
# NOTA: P2/P4 (crisis→hold) y P3 (confidence) NO aplican hoy a estrategias — no hay agent_code,
# confidence ni crisis-flag por cliente; aplicarlos sería ceremonia vacía. Revisar si esos
# sistemas aparecen para estrategias (ver SOURCE §6).

from __future__ import annotations
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from app.workers.base_worker import BaseWorker
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_billing.application.credits_service import check_budget
from app.bc_cognition.domain.strategy_cadence import cadence_for, should_generate_on
from app.bc_cognition.application.use_generate_strategy import use_generate_strategy

logger = logging.getLogger(__name__)
_TZ = ZoneInfo("America/Puerto_Rico")


class StrategyGeneratorWorker(BaseWorker):
    """1 estrategia automática por cadencia/cliente · idempotente por (cliente, día)."""

    name = "strategy_generator"

    async def execute(self, client_id: str) -> dict:
        supabase = get_supabase_service()
        level = self._level_for(supabase, client_id)
        today = datetime.now(_TZ)
        # belt-and-suspenders · TODO chequeo barato ANTES de generar (Claude cuesta $):
        if not should_generate_on(level, today.weekday()):          # 1 · cadence
            return {"skipped": "cadence", "level": level}
        cadence = cadence_for(level)
        key = f"{client_id}:{today.date().isoformat()}"
        if self._already_generated(supabase, key):                  # 2 · idempotencia (pre-SELECT · evita gasto)
            return {"skipped": "idempotent", "key": key}
        if not await check_budget(client_id):                       # 3 · budget (NO se hereda del handler)
            return {"skipped": "budget", "key": key}
        result, err = await use_generate_strategy(                  # 4 · generar (caro · solo si pasó 1-3)
            client_id, tipo=cadence, generation_key=key)            # 5 · upsert ON CONFLICT (red de carrera · en el repo)
        if err or not result:
            raise RuntimeError(err.message if err else "strategy gen sin resultado")  # → circuit breaker
        return {"generated": result.id, "tipo": cadence, "key": key}

    def _level_for(self, supabase, client_id: str) -> int:
        try:
            r = supabase.client.table("clients").select("aria_level").eq("id", client_id).limit(1).execute()
            return (r.data[0].get("aria_level") if r.data else 1) or 1
        except Exception:
            return 1

    def _already_generated(self, supabase, key: str) -> bool:
        try:
            r = supabase.client.table("strategies").select("id").eq("generation_key", key).limit(1).execute()
            return bool(r.data)
        except Exception:
            return False  # ante duda → generar; el UNIQUE de la DB (upsert ignore_duplicates) es la red final
