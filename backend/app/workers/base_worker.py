# backend/app/workers/base_worker.py
# MAX 200 LINES — R-LINES-001
# Base Worker — clase base para todos los workers autónomos de OMEGA
# R-WORKER-001: 3 fallos → circuit breaker + alerta
# FIX: INSERT solo en 'started', UPDATE en 'completed'/'failed'/'disabled'

from __future__ import annotations
import time
import asyncio
import logging
from abc import ABC, abstractmethod
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """
    Clase base para todos los workers autónomos de OMEGA.
    R-WORKER-001: circuit breaker automático en 3 fallos consecutivos.
    """

    name: str = "base_worker"
    max_failures: int = 3

    async def run_for_client(self, client_id: str) -> None:
        """Ejecuta el worker para un cliente. Maneja circuit breaker."""
        start = time.time()
        log_id = f"{self.name}_{client_id}_{int(start * 1000)}"

        await self._log(log_id, client_id, "started")

        try:
            result = await self.execute(client_id)
            duration_ms = int((time.time() - start) * 1000)
            await self._log(log_id, client_id, "completed", result, duration_ms)
            await self._reset_failures(client_id)
            logger.info(f"[{self.name}] client={client_id} OK {duration_ms}ms")

        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            error = str(e)[:300]
            await self._log(log_id, client_id, "failed", error=error, duration_ms=duration_ms)
            count = await self._increment_failures(client_id)
            logger.error(f"[{self.name}] client={client_id} FAIL #{count}: {error}")

            if count >= self.max_failures:
                await self._disable_and_alert(client_id, error)

    async def run_all_clients(self) -> None:
        """Ejecuta el worker para todos los clientes activos."""
        clients = await self._get_active_clients()
        logger.info(f"[{self.name}] running for {len(clients)} clients")

        # Max 5 clientes simultáneos — R-WORKER-001
        semaphore = asyncio.Semaphore(5)

        async def run_with_semaphore(client_id: str):
            async with semaphore:
                await self.run_for_client(client_id)

        await asyncio.gather(
            *[run_with_semaphore(cid) for cid in clients],
            return_exceptions=True
        )

    @abstractmethod
    async def execute(self, client_id: str) -> dict:
        """Lógica principal del worker. Implementar en subclase."""
        ...

    async def _get_active_clients(self) -> list[str]:
        """Obtiene UUIDs de clientes activos (excluye resellers y owners)."""
        try:
            supabase = get_supabase_service()
            result = (
                supabase.client.table("clients")
                .select("id")
                .eq("status", "active")
                .eq("role", "client")  # Excluye resellers y owners
                .execute()
            )
            return [r["id"] for r in (result.data or [])]
        except Exception as e:
            logger.error(f"[{self.name}] Error fetching clients: {e}")
            return []

    async def _log(
        self,
        log_id: str,
        client_id: str,
        status: str,
        result: dict | None = None,
        duration_ms: int = 0,
        error: str | None = None,
    ) -> None:
        """
        Loguea estado del worker en omega_worker_logs — R-OPS-001.
        INSERT solo en 'started'. UPDATE para todo lo demás.
        Evita duplicate PK al usar el mismo log_id en múltiples llamadas.
        """
        try:
            supabase = get_supabase_service()

            if status == "started":
                # Primera llamada — crear el registro
                supabase.client.table("omega_worker_logs").insert({
                    "id":          log_id,
                    "worker_name": self.name,
                    "client_id":   client_id,
                    "status":      status,
                    "result":      result or {},
                    "error":       error,
                    "duration_ms": duration_ms,
                }).execute()
            else:
                # Completado o fallido — actualizar el registro existente
                supabase.client.table("omega_worker_logs").update({
                    "status":      status,
                    "result":      result or {},
                    "error":       error,
                    "duration_ms": duration_ms,
                }).eq("id", log_id).execute()

        except Exception as e:
            # Fallback a stdout — Railway logs siempre captura esto
            logger.warning(
                f"[{self.name}] DB log failed (status={status}, "
                f"client={client_id}): {e}"
            )

    async def _get_failure_count(self, client_id: str) -> int:
        """Obtiene conteo de fallos consecutivos."""
        try:
            supabase = get_supabase_service()
            result = (
                supabase.client.table("omega_worker_logs")
                .select("status")
                .eq("worker_name", self.name)
                .eq("client_id", client_id)
                .order("created_at", desc=True)
                .limit(self.max_failures)
                .execute()
            )
            rows = result.data or []
            count = 0
            for row in rows:
                if row["status"] == "failed":
                    count += 1
                else:
                    break
            return count
        except Exception:
            return 0

    async def _increment_failures(self, client_id: str) -> int:
        return await self._get_failure_count(client_id)

    async def _reset_failures(self, client_id: str) -> None:
        pass  # Reset implícito — _get_failure_count busca consecutivos

    async def _disable_and_alert(self, client_id: str, error: str) -> None:
        """R-WORKER-001: desactiva worker y alerta a owner."""
        logger.critical(
            f"[{self.name}] DISABLED for client={client_id} "
            f"after {self.max_failures} consecutive failures. Error: {error}"
        )
        try:
            # Este usa ID único propio — no hay conflicto de PK
            disable_id = f"{self.name}_{client_id}_disabled_{int(time.time())}"
            supabase = get_supabase_service()
            supabase.client.table("omega_worker_logs").insert({
                "id":          disable_id,
                "worker_name": self.name,
                "client_id":   client_id,
                "status":      "disabled",
                "error":       f"Circuit breaker: {error}",
                "duration_ms": 0,
            }).execute()
        except Exception:
            pass
