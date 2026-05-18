"""OmegaRaisen — Image Generation Compat Layer (Fase 2 §2.4 + §2.6).

Mediates between Lovable callers expecting `List[str]` of URLs (DALL-E 3
shape) and the Nano Banana V3 adapter which returns base64 inline. This
layer currently returns data URIs; production deployment requires uploading
to Supabase Storage and returning public URLs (see DEBT-018).

Supports `reference_images_b64` for edit mode (post §2.6 swap of FAL Flux
Kontext to Nano Banana refs · cierra DEBT-022).
"""
from __future__ import annotations

from typing import List, Optional

from app.bc_cognition.infrastructure._nano_banana_types import ImageRoute
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
) -> List[str]:
    """Lovable-compatible image generation backed by Nano Banana.

    Returns a list of data URIs (`data:<mime>;base64,<payload>`). For
    production deployment these should be uploaded to Supabase Storage
    and replaced with public URLs (DEBT-018).

    If `reference_images_b64` is provided, Nano Banana uses them as visual
    context (edit mode · max 20 images per Nano Banana adapter limit).
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
        data_uris.append(
            f"data:{response.mime_type};base64,{response.image_b64}"
        )
    return data_uris
