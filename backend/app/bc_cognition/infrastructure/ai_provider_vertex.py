"""AI Provider · Google Vertex (failover · not_configured hasta env vars + SDK · Capa 7-A).

V1: si no está anthropic[vertex] o faltan las Google env vars → configured=False. La llamada
real (AnthropicVertex) se implementa en 7-B. I1-consistente: Vertex sirve el MISMO Claude.
"""
from __future__ import annotations

import os
from typing import Any, Optional

try:
    from anthropic import AnthropicVertex  # noqa: F401
    _VERTEX_OK = True
except Exception:
    _VERTEX_OK = False

_MODEL_MAP = {
    "claude-sonnet-4-6": "claude-sonnet-4-6@20250514",
}


def _vertex_env_present() -> bool:
    return bool(
        os.environ.get("GOOGLE_VERTEX_PROJECT_ID")
        and os.environ.get("GOOGLE_VERTEX_LOCATION")
        and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    )


class VertexProvider:
    name = "vertex"

    @property
    def configured(self) -> bool:
        return _VERTEX_OK and _vertex_env_present()

    @property
    def reason_not_configured(self) -> Optional[str]:
        if not _VERTEX_OK:
            return "anthropic[vertex] sdk_missing"
        if not _vertex_env_present():
            return "Google Vertex env vars missing"
        return None

    async def call(self, create_kwargs: dict[str, Any]):
        # Safety net · el router solo invoca providers configured (7-B implementa el call real).
        raise RuntimeError("Vertex no implementado en 7-A (activar en 7-B)")
