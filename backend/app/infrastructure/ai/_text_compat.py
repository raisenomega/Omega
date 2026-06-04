"""
_text_compat.py

Bridge temporal generate_text() legacy -> anthropic_adapter.generate().
Permite migracion incremental de los callers de claude_service durante DEBT-024.

Preserva defaults legacy (temperature=0.7 - max_tokens=4096) para no driftar
comportamiento en callers que omiten esos params.

Una vez migrados los 51 callers, este bridge se evalua:
  - Mantener: si simplifica el contract para nuevos callers no-DDD.
  - Eliminar: si TODOS los nuevos callers deben usar adapter.generate directo.
Decision final post cierre DEBT-024.
"""
from typing import Optional

from app.bc_cognition.infrastructure.anthropic_adapter import generate as _adapter_generate


async def generate_text(
    agent_code: str,
    prompt: str,
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Bridge legacy generate_text -> anthropic_adapter.generate.

    Args:
        agent_code: Routing key (ej: "growth_hacker"). Resuelve modelo via routing_table.
        prompt: Mensaje user para Claude.
        system_message: System prompt opcional (default None -> "").
        temperature: 0.7 (preserva default claude_service).
        max_tokens: 4096 (preserva default claude_service).

    Returns:
        str: Texto generado por Claude.

    Raises:
        RuntimeError: Si el adapter retorna error. Preserva el contract
                      raise-on-error de claude_service legacy.
    """
    response, error = await _adapter_generate(
        agent_code=agent_code,
        system=system_message or "",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if error is not None:
        raise RuntimeError(f"[{error.code}] {error.message}")
    if response is None:
        raise RuntimeError("anthropic_adapter returned (None, None) - invalid Result tuple")

    return response.text
