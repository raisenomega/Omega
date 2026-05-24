"""
OmegaRaisen — Nano Banana Adapter (ÚNICO entry GENERACIÓN IMÁGENES · DDD I1 exception)

Excepción documentada, aprobada owner 17 may 2026.
Re-evaluación: Q4 2026 si Anthropic lanza generación de imágenes nativa.

Tipos y routing: _nano_banana_types.py
"""

from __future__ import annotations

import base64
import os
import time

from google import genai
from google.genai import types

from app.bc_cognition.infrastructure._nano_banana_types import (
    ImageRoute, MODEL_BY_ROUTE, ImageResponse, ImageError,
)

# google-genai 2.6 ImageConfig.aspect_ratio · supported values (DEBT-CL-011)
_VALID_ASPECT_RATIOS: frozenset[str] = frozenset({
    "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", "21:9",
})

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY no configurada")
        _client = genai.Client(api_key=key)
    return _client


async def generate(
    prompt: str,
    route: ImageRoute = "default",
    reference_images_b64: list[str] | None = None,
    aspect_ratio: str = "1:1",
) -> tuple[ImageResponse | None, ImageError | None]:
    """Genera imagen vía Nano Banana. aspect_ratio: 1:1|16:9|9:16|4:3|21:9."""
    if not prompt or len(prompt) > 8000:
        return None, ImageError("invalid_input", "prompt vacío o >8000 chars")
    if aspect_ratio not in _VALID_ASPECT_RATIOS:
        return None, ImageError("invalid_input", f"aspect_ratio '{aspect_ratio}' no soportado")

    model = MODEL_BY_ROUTE[route]
    contents: list = [prompt]
    if reference_images_b64:
        for img in reference_images_b64[:20]:                       # max 20 refs
            contents.append(types.Part.from_bytes(
                data=base64.b64decode(img), mime_type="image/png",
            ))

    start = time.monotonic()
    try:
        resp = await _get_client().aio.models.generate_content(
            model=model,
            contents=contents,
            # DEBT-CL-011 cerrada (23 may 2026 · Sprint 3): google-genai 2.6
            # trajo types.ImageConfig de vuelta · aspect_ratio honrado por SDK.
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )
    except Exception as e:                                          # noqa: BLE001
        return None, ImageError("api_error", str(e))

    latency_ms = int((time.monotonic() - start) * 1000)
    for part in resp.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            return ImageResponse(
                image_b64=base64.b64encode(part.inline_data.data).decode("ascii"),
                mime_type=part.inline_data.mime_type or "image/png",
                model_used=model,
                latency_ms=latency_ms,
            ), None
    return None, ImageError("safety_block", "Sin imagen en response (posible safety filter)")
