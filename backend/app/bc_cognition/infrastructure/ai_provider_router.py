"""AIProviderRouter (Capa 7-A) · failover Anthropic→Bedrock→Vertex + circuit breaker + telemetría.

Singleton lazy (patrón _client del adapter). El adapter delega su llamada de red a execute().
V1: solo Anthropic activo (bedrock/vertex not_configured) → comportamiento byte-idéntico a hoy.
execute() re-lanza la excepción original en fallo total → los except del adapter siguen igual.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.infrastructure.ai_provider_anthropic import AnthropicProvider
from app.bc_cognition.infrastructure.ai_provider_bedrock import BedrockProvider
from app.bc_cognition.infrastructure.ai_provider_vertex import VertexProvider

logger = logging.getLogger(__name__)

_CB_THRESHOLD = 5       # fallas consecutivas → abre el circuito
_CB_OPEN_SECONDS = 60   # tiempo abierto antes de half-open


class AIProviderRouter:
    def __init__(self):
        self.providers = [AnthropicProvider(), BedrockProvider(), VertexProvider()]
        self._fails: Dict[str, int] = {}
        self._open_until: Dict[str, float] = {}

    def circuit_open(self, name: str, now: float) -> bool:
        return self._open_until.get(name, 0) > now

    def _record(self, name: str, ok: bool, now: float) -> None:
        if ok:
            self._fails[name] = 0
            self._open_until.pop(name, None)
        else:
            self._fails[name] = self._fails.get(name, 0) + 1
            if self._fails[name] >= _CB_THRESHOLD:
                self._open_until[name] = now + _CB_OPEN_SECONDS

    def _log(self, provider: str, model: str, agent_code: str, status: str,
             latency_ms: Optional[int], err: Optional[str]) -> None:
        try:
            get_supabase_service().client.table("ai_provider_calls").insert({
                "provider": provider, "model": model, "agent_code": agent_code,
                "status": status, "latency_ms": latency_ms, "error": err,
            }).execute()
        except Exception as e:
            logger.warning(f"ai_provider_calls insert skip (best-effort): {e}")

    async def execute(self, create_kwargs: Dict[str, Any], timeout_s: float, agent_code: str):
        model = create_kwargs.get("model", "")
        now = time.monotonic()
        active = [p for p in self.providers if p.configured and not self.circuit_open(p.name, now)]
        if not active:
            raise RuntimeError("No hay AI provider disponible (no-configurados o circuito abierto)")
        last_exc: Optional[Exception] = None
        for i, p in enumerate(active):
            start = time.monotonic()
            try:
                resp = await asyncio.wait_for(p.call(create_kwargs), timeout=timeout_s)
                self._record(p.name, True, time.monotonic())
                self._log(p.name, model, agent_code, "success", int((time.monotonic() - start) * 1000), None)
                return resp
            except Exception as e:  # noqa: BLE001 · failover sobre cualquier fallo del provider
                self._record(p.name, False, time.monotonic())
                self._log(p.name, model, agent_code, "failed", int((time.monotonic() - start) * 1000), str(e)[:300])
                last_exc = e
                if i < len(active) - 1:
                    self._log(p.name, model, agent_code, "failover_triggered", None, f"-> {active[i + 1].name}")
                    logger.warning(f"AI failover: {p.name} falló → {active[i + 1].name}")
        raise last_exc if last_exc else RuntimeError("AI provider sin respuesta")


_router: Optional[AIProviderRouter] = None


def get_ai_provider_router() -> AIProviderRouter:
    global _router
    if _router is None:
        _router = AIProviderRouter()
    return _router


async def execute(create_kwargs: Dict[str, Any], timeout_s: float, agent_code: str):
    """Entry point que invoca el adapter · delega al singleton."""
    return await get_ai_provider_router().execute(create_kwargs, timeout_s, agent_code)
