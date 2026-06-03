"""AI Provider · AWS Bedrock (failover · not_configured hasta env vars + SDK · Capa 7-A).

V1: si no hay boto3 instalado o faltan las AWS env vars → configured=False (el router no lo
incluye en el loop). La llamada real a bedrock-runtime se implementa en 7-B. I1-consistente:
Bedrock sirve el MISMO modelo Claude, distinta infra.
"""
from __future__ import annotations

import os
from typing import Any, Optional

try:
    import boto3  # noqa: F401
    _BOTO3_OK = True
except Exception:
    _BOTO3_OK = False

# OMEGA model id → Bedrock model id (se completa al activar 7-B).
_MODEL_MAP = {
    "claude-sonnet-4-6": "anthropic.claude-sonnet-4-6-20250514-v1:0",
}


def _aws_env_present() -> bool:
    return bool(
        os.environ.get("AWS_ACCESS_KEY_ID")
        and os.environ.get("AWS_SECRET_ACCESS_KEY")
        and os.environ.get("AWS_REGION")
    )


class BedrockProvider:
    name = "bedrock"

    @property
    def configured(self) -> bool:
        return _BOTO3_OK and _aws_env_present()

    @property
    def reason_not_configured(self) -> Optional[str]:
        if not _BOTO3_OK:
            return "boto3 sdk_missing"
        if not _aws_env_present():
            return "AWS env vars missing"
        return None

    async def call(self, create_kwargs: dict[str, Any]):
        # Safety net · el router solo invoca providers configured (7-B implementa el invoke real).
        raise RuntimeError("Bedrock no implementado en 7-A (activar en 7-B)")
