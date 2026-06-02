"""Nano Banana Adapter · ÚNICO entry GENERACIÓN IMÁGENES (DDD I1 exception · aprobada owner
17 may 2026 · re-eval Q4 2026 si Anthropic lanza imágenes nativo). Tipos y routing: _nano_banana_types.py."""

from __future__ import annotations

import asyncio
import base64
import os
import time

from google import genai
from google.genai import types

from app.bc_cognition.infrastructure._nano_banana_types import (
    ImageRoute, MODEL_BY_ROUTE, ImageResponse, ImageError,
    MAX_ATTEMPTS, classify_error, backoff_delay,            # DEBT-071
)
from app.bc_cognition.infrastructure.hermes_usage import record_mcp_use  # HERMES f1.5 · usage-tracking

# google-genai 2.6 ImageConfig.aspect_ratio · supported values (DEBT-CL-011)
_VALID_ASPECT_RATIOS: frozenset[str] = frozenset({
    "1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", "21:9",
})

# DEBT-069 · asyncio.wait_for cap sobre SDK google-genai (28 may: 90→120→180s · parche DEBT-IMAGE-ASYNC).
_GENERATION_TIMEOUT_S: float = 180.0

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

    # DEBT-CL-011: google-genai 2.6 → types.ImageConfig honra aspect_ratio en el SDK.
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
    )
    # DEBT-071: retry transitorios (429/5xx) · 1 retry timeout en attempt 0 (sleep 5s · NO en errores de contenido).
    for attempt in range(MAX_ATTEMPTS):
        start = time.monotonic()
        try:
            resp = await asyncio.wait_for(
                _get_client().aio.models.generate_content(model=model, contents=contents, config=config),
                timeout=_GENERATION_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            if attempt == 0:
                await asyncio.sleep(5.0); continue
            return None, ImageError("timeout", f"Nano Banana excedió {_GENERATION_TIMEOUT_S:.0f}s")
        except Exception as e:                                      # noqa: BLE001
            kind = classify_error(e)
            if kind in ("rate_limited", "transient") and attempt < MAX_ATTEMPTS - 1:
                await asyncio.sleep(backoff_delay(attempt))
                continue
            record_mcp_use("nano_banana", ok=False, detail=str(e)[:80])  # HERMES f1.5
            return None, ImageError("rate_limited" if kind == "rate_limited" else "api_error", str(e))

        latency_ms = int((time.monotonic() - start) * 1000)
        cands = resp.candidates or []
        parts = (cands[0].content.parts if cands and cands[0].content else None) or []
        for part in parts:
            if part.inline_data and part.inline_data.data:
                record_mcp_use("nano_banana", ok=True)  # HERMES f1.5
                return ImageResponse(
                    image_b64=base64.b64encode(part.inline_data.data).decode("ascii"),
                    mime_type=part.inline_data.mime_type or "image/png",
                    model_used=model,
                    latency_ms=latency_ms,
                ), None
        return None, ImageError("safety_block", "Sin imagen en response (posible safety filter)")
    return None, ImageError("api_error", "Nano Banana: reintentos agotados")
