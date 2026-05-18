"""OmegaRaisen — Tipos del Veo 3.1 adapter (split para cumplir C4)."""

from dataclasses import dataclass
from typing import Literal

VideoRoute = Literal["default", "cheap"]

MODEL_BY_ROUTE: dict[VideoRoute, str] = {
    "default": "veo-3.1-generate-preview",          # 8s 720/1080/4K · audio nativo
    "cheap":   "veo-3.1-lite-generate-preview",     # 50% cost de Fast, mismo speed
}


@dataclass(frozen=True)
class VideoOperation:
    """Handle a una operación async. Pasar a poll() para verificar estado."""
    operation_name: str
    model_used: str
    started_at: float


@dataclass(frozen=True)
class VideoResult:
    video_uri: str            # URI temporal de Google (descargar antes de TTL)
    duration_s: int           # 8 (Veo 3.1 produce 8s)
    has_audio: bool
    model_used: str
    total_latency_s: int


@dataclass(frozen=True)
class VideoError:
    code: str                 # 'timeout' | 'safety_block' | 'api_error' | 'invalid_input'
    message: str
