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
import os
import time
from typing import Any

from anthropic import AsyncAnthropic, APIError, APITimeoutError

from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA
from app.bc_cognition.domain.routing_table import resolve_model
from app.bc_cognition.infrastructure._anthropic_types import (
    ClaudeResponse, ClaudeError, estimate_cost,
)

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY no configurada")
        _client = AsyncAnthropic(api_key=key)
    return _client


async def generate(
    agent_code: str,
    system: str,
    messages: list[dict[str, Any]],
    max_tokens: int = 1024,
    temperature: float = 1.0,
) -> tuple[ClaudeResponse | None, ClaudeError | None]:
    """Llama a Claude resolviendo modelo por agent_code. Nunca lanza."""
    try:
        model = resolve_model(agent_code)
    except KeyError:
        return None, ClaudeError("invalid_input", f"agent_code '{agent_code}' no registrado")

    timeout_s = LIMITS_OMEGA["MAX_CLAUDE_LATENCY_MS"] / 1000
    start = time.monotonic()
    try:
        resp = await asyncio.wait_for(
            _get_client().messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=[{"type": "text", "text": system,
                         "cache_control": {"type": "ephemeral"}}],     # I3
                messages=messages,
            ),
            timeout=timeout_s,
        )
    except asyncio.TimeoutError:
        return None, ClaudeError("timeout", f"Excedió {timeout_s}s")
    except APITimeoutError as e:
        return None, ClaudeError("timeout", str(e))
    except APIError as e:
        return None, ClaudeError("api_error", str(e), retry_after_s=getattr(e, "retry_after", None))

    text = "".join(b.text for b in resp.content if b.type == "text")
    cache_read = getattr(resp.usage, "cache_read_input_tokens", 0) or 0
    in_tok, out_tok = resp.usage.input_tokens, resp.usage.output_tokens
    return ClaudeResponse(
        text=text, model_used=model,
        input_tokens=in_tok, output_tokens=out_tok,
        cost_usd=estimate_cost(model, in_tok, out_tok),
        latency_ms=int((time.monotonic() - start) * 1000),
        cache_hit=cache_read > 0,
    ), None
