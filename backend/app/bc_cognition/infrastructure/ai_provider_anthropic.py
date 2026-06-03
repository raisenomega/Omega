"""AI Provider · Anthropic (primario · siempre configurado si hay API key). Capa 7-A.

Encapsula el AsyncAnthropic client (movido íntegro desde anthropic_adapter · lazy-singleton).
call() deja propagar APIError/APITimeoutError al router (que decide failover / re-lanza).
"""
from __future__ import annotations

import os
from typing import Any, Optional

from anthropic import AsyncAnthropic

_client: Optional[AsyncAnthropic] = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY no configurada")
        _client = AsyncAnthropic(api_key=key)
    return _client


class AnthropicProvider:
    name = "anthropic"

    @property
    def configured(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    @property
    def reason_not_configured(self) -> Optional[str]:
        return None if self.configured else "ANTHROPIC_API_KEY missing"

    async def call(self, create_kwargs: dict[str, Any]):
        """messages.create directo · sin timeout propio (lo aplica el router con wait_for)."""
        return await _get_client().messages.create(**create_kwargs)
