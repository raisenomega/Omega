"""OmegaRaisen — Video Generation Compat Layer (Fase 2 §2.5 + Sprint 2 DEBT-019).

Mediates entre callers legacy (Dict[str, Any] · shape de video V1) y Veo 3.1 V3 adapter
LRO. Descarga bytes del temp Google URI antes de TTL + upload a Supabase Storage
→ retorna URL persistente (cierra DEBT-019 · 22 may 2026).

DEBT-020 (background-job pattern) sigue abierta · sync polling 300s puede timeout
en Vercel (frontend). Para producción real usar job queue + GET status endpoint.
"""
from __future__ import annotations

import os
from typing import Dict, Optional

import httpx

from app.bc_cognition.infrastructure._storage_uploader import (
    StorageUploadError, upload_video_bytes,
)
from app.bc_cognition.infrastructure.veo3_adapter import (
    poll as _veo3_poll,
    start_generation as _veo3_start,
)

_RATIO_TO_ASPECT: Dict[str, str] = {
    "1280:768": "16:9",
    "768:1280": "9:16",
    "1024:1024": "16:9",  # Veo 3.1 no produce 1:1; fallback landscape
}
_DEFAULT_ASPECT = "16:9"
_VIDEO_MIME = "video/mp4"
_DOWNLOAD_TIMEOUT_S = 120


async def generate_video_compat(
    prompt: str,
    duration: int = 5,
    ratio: str = "1280:768",
    client_id: Optional[str] = None,
    logo_url: Optional[str] = None,
) -> Dict[str, object]:
    """Video generation (compat V1) backed by Veo 3.1 + Supabase Storage.

    `duration` aceptado por compat (Veo 3.1 siempre 8s). `ratio` mapeado a aspect.
    `client_id` opcional · None → folder 'shared/' (legacy · LV1 handler).

    Cierra DEBT-019: video_url devuelto es URL persistente Storage (no Google
    temp). Si download/upload falla → status='failed'. DEBT-020 sigue abierta
    (sync poll 300s puede timeout en Vercel · job queue pendiente).
    """
    _ = duration  # Veo 3.1 always 8s
    aspect_ratio = _RATIO_TO_ASPECT.get(ratio, _DEFAULT_ASPECT)

    operation, start_err = await _veo3_start(prompt=prompt, aspect_ratio=aspect_ratio)
    if start_err is not None or operation is None:
        return {"status": "failed", "error": start_err.message if start_err else "no operation"}

    result, poll_err = await _veo3_poll(operation, max_wait_s=300)
    if poll_err is not None or result is None:
        return {"status": "failed", "error": poll_err.message if poll_err else "no result"}

    try:
        video_bytes = await _download_veo_uri(result.video_uri)
        if logo_url:  # DEBT-FFMPEG · overlay best-effort (FFmpeg ausente → bytes intactos)
            from app.bc_cognition.infrastructure._logo_overlay_video import (
                apply_logo_to_video_bytes,
            )
            video_bytes = await apply_logo_to_video_bytes(video_bytes, logo_url)
        public_url = await upload_video_bytes(video_bytes, _VIDEO_MIME, client_id=client_id)  # DEBT-068
    except (httpx.HTTPError, StorageUploadError) as e:
        return {"status": "failed", "error": f"persist_failed: {e}"}

    return {
        "status": "completed",
        "video_url": public_url,
        "model": result.model_used,
        "duration": result.duration_s,
        "ratio": ratio,
        "task_id": operation.operation_name,
    }


async def _download_veo_uri(uri: str) -> bytes:
    """HTTP GET con API key Gemini · Veo URIs requieren x-goog-api-key header."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise httpx.HTTPError("GEMINI_API_KEY no configurada para download")
    async with httpx.AsyncClient(timeout=_DOWNLOAD_TIMEOUT_S, follow_redirects=True) as client:
        r = await client.get(uri, headers={"x-goog-api-key": api_key})
        r.raise_for_status()
        return r.content
