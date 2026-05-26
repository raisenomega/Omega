"""OmegaRaisen — Tipos + helpers de resiliencia del Nano Banana adapter (split C4)."""

import random
from dataclasses import dataclass
from typing import Literal

ImageRoute = Literal["default", "premium", "cheap"]

MODEL_BY_ROUTE: dict[ImageRoute, str] = {
    "default": "gemini-3.1-flash-image-preview",   # Nano Banana 2 — workhorse
    "premium": "gemini-3-pro-image-preview",       # Pro — text/diagrams brand-critical
    "cheap":   "gemini-2.5-flash-image",           # Legacy — bulk 1K
}


@dataclass(frozen=True)
class ImageResponse:
    image_b64: str            # PNG base64
    mime_type: str
    model_used: str
    latency_ms: int


@dataclass(frozen=True)
class ImageError:
    code: str                 # 'timeout'|'rate_limited'|'safety_block'|'api_error'|'invalid_input'
    message: str


# ─── DEBT-071: retry/backoff para errores transitorios del SDK Google ────
MAX_ATTEMPTS: int = 2         # intento + 1 reintento
_BACKOFF_BASE_S: float = 0.5


def classify_error(e: Exception) -> str:
    """'rate_limited' (429/quota) · 'transient' (5xx) · 'api_error' (resto · no se reintenta)."""
    text = f"{getattr(e, 'code', '')} {getattr(e, 'status', '')} {e}".lower()
    if "429" in text or "resource_exhausted" in text or "quota" in text or "rate limit" in text:
        return "rate_limited"
    if any(s in text for s in ("500", "502", "503", "504", "unavailable", "internal", "deadline")):
        return "transient"
    return "api_error"


def backoff_delay(attempt: int) -> float:
    """Backoff exponencial + jitter (segundos) antes del reintento."""
    return _BACKOFF_BASE_S * (2 ** attempt) + random.uniform(0.0, 0.3)
