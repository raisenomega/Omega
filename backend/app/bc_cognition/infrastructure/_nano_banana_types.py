"""OmegaRaisen — Tipos del Nano Banana adapter (split para cumplir C4)."""

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
    code: str                 # 'timeout' | 'safety_block' | 'api_error' | 'invalid_input'
    message: str
