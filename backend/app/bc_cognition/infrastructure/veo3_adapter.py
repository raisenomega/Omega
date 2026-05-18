"""
OmegaRaisen — Veo 3.1 Adapter (ÚNICO entry GENERACIÓN VIDEO · DDD I1 exception)

Excepción documentada, aprobada owner 17 may 2026.
Re-evaluación: Q4 2026 si Anthropic lanza generación de video nativa.

Video generation es ASYNC (LRO). Caller hace start_generation() y luego poll().
Tipos y routing: _veo3_types.py
"""

from __future__ import annotations

import asyncio
import base64
import os
import time

from google import genai
from google.genai import types

from app.bc_cognition.infrastructure._veo3_types import (
    VideoRoute, MODEL_BY_ROUTE, VideoOperation, VideoResult, VideoError,
)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY no configurada")
        _client = genai.Client(api_key=key)
    return _client


async def start_generation(
    prompt: str,
    route: VideoRoute = "default",
    reference_image_b64: str | None = None,
    aspect_ratio: str = "16:9",
) -> tuple[VideoOperation | None, VideoError | None]:
    """Lanza generación. Retorna handle para poll(), NO espera completion."""
    if not prompt or len(prompt) > 4000:
        return None, VideoError("invalid_input", "prompt vacío o >4000 chars")

    model = MODEL_BY_ROUTE[route]
    cfg: dict = {"aspect_ratio": aspect_ratio}
    if reference_image_b64:
        cfg["reference_images"] = [types.Image(
            image_bytes=base64.b64decode(reference_image_b64),
            mime_type="image/png",
        )]

    try:
        op = await _get_client().aio.models.generate_videos(
            model=model,
            prompt=prompt,
            config=types.GenerateVideosConfig(**cfg),
        )
    except Exception as e:                                          # noqa: BLE001
        return None, VideoError("api_error", str(e))

    return VideoOperation(
        operation_name=op.name,
        model_used=model,
        started_at=time.monotonic(),
    ), None


async def poll(
    operation: VideoOperation,
    max_wait_s: int = 300,
    poll_interval_s: int = 10,
) -> tuple[VideoResult | None, VideoError | None]:
    """Polling de completion. Veo 3.1 toma ~30-90s típicamente."""
    deadline = time.monotonic() + max_wait_s
    while time.monotonic() < deadline:
        op = await _get_client().aio.operations.get(operation.operation_name)
        if op.done:
            if op.error:
                return None, VideoError("api_error", str(op.error))
            video = op.response.generated_videos[0]
            return VideoResult(
                video_uri=video.video.uri,
                duration_s=8,
                has_audio=True,
                model_used=operation.model_used,
                total_latency_s=int(time.monotonic() - operation.started_at),
            ), None
        await asyncio.sleep(poll_interval_s)

    return None, VideoError("timeout", f"Excedió {max_wait_s}s sin completar")
