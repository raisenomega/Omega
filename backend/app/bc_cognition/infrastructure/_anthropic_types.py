"""OmegaRaisen — Tipos del Anthropic adapter (split para cumplir C4)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaudeResponse:
    """Resultado exitoso de Claude (immutable)."""
    text: str
    model_used: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int
    cache_hit: bool
    tool_calls: list | None = None   # 1b · bloques tool_use de Claude · None si no hay (aditivo)


@dataclass(frozen=True)
class ClaudeError:
    """Error estructurado — los adapters nunca lanzan excepción al caller."""
    code: str                  # 'timeout' | 'rate_limited' | 'api_error' | 'invalid_input'
    message: str
    retry_after_s: int | None = None


# USD por 1M tokens (input, output) · ratios verificados mayo 2026
_RATES: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-sonnet-4-6":         (3.00, 15.00),
    "claude-opus-4-7":          (15.00, 75.00),
}


def estimate_cost(model: str, in_tokens: int, out_tokens: int) -> float:
    """Estimación grosera USD — tracking, no facturación."""
    rate_in, rate_out = _RATES.get(model, (3.00, 15.00))
    return (in_tokens * rate_in + out_tokens * rate_out) / 1_000_000
