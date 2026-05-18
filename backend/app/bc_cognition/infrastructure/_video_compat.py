"""OmegaRaisen — Video Generation Compat Layer (Fase 2 §2.5).

Mediates between Lovable callers expecting a `Dict[str, Any]` response (Runway
shape) and the Veo 3.1 V3 adapter which exposes an async LRO (`start +
poll`). This layer hides the polling internally and returns the temporary
Google URI; production deployment requires Supabase Storage upload (DEBT-019)
and a background-job pattern (DEBT-020) to avoid HTTP timeouts.
"""
from __future__ import annotations

from typing import Dict

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


async def generate_video_compat(
    prompt: str,
    duration: int = 5,
    ratio: str = "1280:768",
) -> Dict[str, object]:
    """Lovable-compatible video generation backed by Veo 3.1.

    `duration` is accepted for API compatibility but ignored — Veo 3.1
    always produces 8-second videos. `ratio` is mapped to Veo's
    `aspect_ratio` parameter.

    Returns a dict matching the shape of `RunwayAgent.execute()`:
      `{status, video_url, model, duration, ratio, task_id}` on success
      `{status: "failed", error: str}` on any failure.

    The returned `video_url` is a temporary Google URI (TTL — DEBT-019).
    Total wait is bounded at 300s; if Veo doesn't complete within that,
    a `failed` dict with `error="timeout"` is returned.
    """
    _ = duration  # Veo 3.1 always 8s
    aspect_ratio = _RATIO_TO_ASPECT.get(ratio, _DEFAULT_ASPECT)

    operation, start_err = await _veo3_start(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
    )
    if start_err is not None or operation is None:
        message = start_err.message if start_err else "no operation returned"
        return {"status": "failed", "error": message}

    result, poll_err = await _veo3_poll(operation, max_wait_s=300)
    if poll_err is not None or result is None:
        message = poll_err.message if poll_err else "no result returned"
        return {"status": "failed", "error": message}

    return {
        "status": "completed",
        "video_url": result.video_uri,
        "model": result.model_used,
        "duration": result.duration_s,
        "ratio": ratio,
        "task_id": operation.operation_name,
    }
