"""
OmegaRaisen — Anthropic Adapter (ÚNICO entry point Claude · DDD I1)

  · Resolver model_id desde agent_code (routing_table)
  · cache_control: ephemeral en system block (I3)
  · Timeout enforcement (LIMITS_OMEGA)
  · Retorna Result-tuple — nunca lanza al caller

Tipos y pricing: _anthropic_types.py
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from anthropic import APIError, APITimeoutError

from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA
from app.bc_cognition.domain.routing_table import resolve_model
from app.bc_cognition.infrastructure.hermes_usage import record_mcp_use  # HERMES f1.5 · usage-tracking
from app.bc_cognition.infrastructure.ai_provider_router import execute as ai_provider_execute  # Capa 7-A
from app.bc_cognition.infrastructure._anthropic_types import (
    ClaudeResponse, ClaudeError, estimate_cost,
)


async def generate(
    agent_code: str,
    system: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 1024,
    temperature: float = 1.0,
    tools: list[dict[str, Any]] | None = None,   # 1b · None → ruta byte-idéntica a hoy
) -> tuple[ClaudeResponse | None, ClaudeError | None]:
    """Llama a Claude resolviendo modelo por agent_code. Nunca lanza."""
    try:
        model = resolve_model(agent_code)
    except KeyError:
        return None, ClaudeError("invalid_input", f"agent_code '{agent_code}' no registrado")

    timeout_s = LIMITS_OMEGA["MAX_CLAUDE_LATENCY_MS"] / 1000
    start = time.monotonic()
    create_kwargs: dict[str, Any] = {
        "model": model, "max_tokens": max_tokens, "temperature": temperature,
        "system": [{"type": "text", "text": system,
                    "cache_control": {"type": "ephemeral"}}],     # I3
        "messages": messages,
    }
    if tools is not None:
        create_kwargs["tools"] = tools   # solo si hay tools · sin esto = llamada idéntica a hoy
    try:
        # Capa 7-A · el router aplica el timeout (wait_for) y el failover · re-lanza estos mismos
        # tipos de excepción en fallo total → los except de abajo siguen funcionando igual.
        resp = await ai_provider_execute(create_kwargs, timeout_s, agent_code)
    except asyncio.TimeoutError:
        record_mcp_use("anthropic", ok=False, detail=f"timeout {timeout_s}s")  # HERMES f1.5
        return None, ClaudeError("timeout", f"Excedió {timeout_s}s")
    except APITimeoutError as e:
        record_mcp_use("anthropic", ok=False, detail=f"timeout: {e}")
        return None, ClaudeError("timeout", str(e))
    except APIError as e:
        record_mcp_use("anthropic", ok=False, detail=f"api_error: {e}")
        return None, ClaudeError("api_error", str(e), retry_after_s=getattr(e, "retry_after", None))

    record_mcp_use("anthropic", ok=True)  # HERMES f1.5 · uso exitoso
    text = "".join(b.text for b in resp.content if b.type == "text")
    tool_calls = [b for b in resp.content if getattr(b, "type", None) == "tool_use"] or None
    cache_read = getattr(resp.usage, "cache_read_input_tokens", 0) or 0
    in_tok, out_tok = resp.usage.input_tokens, resp.usage.output_tokens
    return ClaudeResponse(
        text=text, model_used=model,
        input_tokens=in_tok, output_tokens=out_tok,
        cost_usd=estimate_cost(model, in_tok, out_tok),
        latency_ms=int((time.monotonic() - start) * 1000),
        cache_hit=cache_read > 0, tool_calls=tool_calls,
    ), None
