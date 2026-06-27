"""OmegaRaisen — Image Generation Compat Layer (Fase 2 §2.4 + §2.6 + Sprint 2 P1).

Mediates between callers legacy expecting `List[str]` of URLs (shape de
imagen V1) and the Nano Banana V3 adapter which returns base64 inline. Decodes
base64 → bytes → uploads to Supabase Storage via _storage_uploader →
returns public URLs persistentes (cierra DEBT-018 · 22 may 2026).

Supports `reference_images_b64` for edit mode (post §2.6 swap a Nano Banana
refs · cierra DEBT-022).
"""
from __future__ import annotations

import base64
import logging
import time
from typing import List, Optional

from app.bc_cognition.infrastructure._nano_banana_types import ImageRoute
from app.bc_cognition.infrastructure._storage_uploader import upload_image_bytes
from app.bc_cognition.infrastructure.nano_banana_adapter import (
    generate as _nano_banana_generate,
)

_SIZE_TO_ASPECT: dict[str, str] = {
    "1024x1024": "1:1",
    "1024x1792": "9:16",
    "1792x1024": "16:9",
    "1024x1280": "4:5",   # A7 · feed IG vertical (inverso de _ASPECT_TO_SIZE · ambos o cae a 1:1)
}
_DEFAULT_ASPECT = "1:1"

_QUALITY_TO_ROUTE: dict[str, ImageRoute] = {
    "standard": "default",
    "hd": "premium",
}
_DEFAULT_ROUTE: ImageRoute = "default"

logger = logging.getLogger(__name__)


async def generate_images_compat(
    prompts: List[str],
    size: str = "1024x1024",
    quality: str = "standard",
    reference_images_b64: Optional[List[str]] = None,
    client_id: Optional[str] = None,
) -> List[str]:
    """Pieza 1 · A3 · MOTOR N: 1 imagen por prompt DISTINTO de la lista (NO el mismo N veces) → sube cada
    una a Storage → devuelve las N URLs en orden. Lista vacía → [] (no-op defensivo · sin tocar el adapter).
    Imágenes a bucket 'generated-images/{client_id|shared}/{uuid}.{ext}' (post DEBT-018 · URLs persistidas).
    reference_images_b64: contexto edit-mode COMPARTIDO por todas (max 20 · NO encadena · eso es Fase C)."""
    aspect_ratio = _SIZE_TO_ASPECT.get(size, _DEFAULT_ASPECT)
    route = _QUALITY_TO_ROUTE.get(quality, _DEFAULT_ROUTE)
    urls: List[str] = []
    for prompt in prompts:
        response, error = await _nano_banana_generate(
            prompt=prompt, route=route,
            reference_images_b64=reference_images_b64, aspect_ratio=aspect_ratio,
        )
        if error is not None or response is None:
            code = error.code if error else "unknown"
            message = error.message if error else "no response"
            raise RuntimeError(f"Nano Banana generation failed: {code} · {message}")
        image_bytes = base64.b64decode(response.image_b64)
        _t_up = time.monotonic()
        url = await upload_image_bytes(image_bytes, response.mime_type, client_id=client_id)  # DEBT-068
        # DEBT-IMAGE-ASYNC · observabilidad: split del tiempo (Gemini vs nuestro upload) · sin cambiar lógica
        logger.info(
            f"image_gen timing · gemini={response.latency_ms}ms upload="
            f"{int((time.monotonic() - _t_up) * 1000)}ms route={route} model={response.model_used} client={client_id or 'shared'}"
        )
        urls.append(url)
    return urls


async def generate_image_compat(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    n: int = 1,
    reference_images_b64: Optional[List[str]] = None,
    client_id: Optional[str] = None,
) -> List[str]:
    """Compat single (retrocompat DURA · firma intacta para los 4 callers actuales): n copias del MISMO
    prompt (comportamiento legacy intacto · n=1 → 1 imagen idéntica a hoy). Delega en el motor N."""
    return await generate_images_compat(
        [prompt] * max(1, n), size=size, quality=quality,
        reference_images_b64=reference_images_b64, client_id=client_id,
    )
