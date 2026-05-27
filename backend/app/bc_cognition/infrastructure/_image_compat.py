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
}
_DEFAULT_ASPECT = "1:1"

_QUALITY_TO_ROUTE: dict[str, ImageRoute] = {
    "standard": "default",
    "hd": "premium",
}
_DEFAULT_ROUTE: ImageRoute = "default"


async def generate_image_compat(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    n: int = 1,
    reference_images_b64: Optional[List[str]] = None,
    client_id: Optional[str] = None,
) -> List[str]:
    """Image generation (compat V1) backed by Nano Banana + Supabase Storage.

    Returns una lista de URLs públicas persistidas (post DEBT-018 · ya no data URIs).
    Imágenes van a bucket 'generated-images/{client_id|shared}/{uuid}.{ext}'.

    Si `client_id` se provee (V3 handlers), las imágenes van al folder del tenant.
    Sin client_id (legacy callers · LV1 handler · content_creator agent), van a
    'shared/'. No breaking change para callers existentes.

    Si `reference_images_b64` se provee, Nano Banana las usa como contexto visual
    (edit mode · max 20 imágenes per Nano Banana adapter limit).
    """
    aspect_ratio = _SIZE_TO_ASPECT.get(size, _DEFAULT_ASPECT)
    route = _QUALITY_TO_ROUTE.get(quality, _DEFAULT_ROUTE)

    data_uris: List[str] = []
    for _ in range(max(1, n)):
        response, error = await _nano_banana_generate(
            prompt=prompt,
            route=route,
            reference_images_b64=reference_images_b64,
            aspect_ratio=aspect_ratio,
        )
        if error is not None or response is None:
            code = error.code if error else "unknown"
            message = error.message if error else "no response"
            raise RuntimeError(
                f"Nano Banana generation failed: {code} · {message}"
            )
        image_bytes = base64.b64decode(response.image_b64)
        url = await upload_image_bytes(image_bytes, response.mime_type, client_id=client_id)  # DEBT-068
        data_uris.append(url)
    return data_uris
