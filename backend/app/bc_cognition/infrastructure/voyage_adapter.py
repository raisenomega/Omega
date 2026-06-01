"""
OmegaRaisen — Voyage Adapter (ÚNICO entry point voyageai · DDD I1 exc 3)

  · Embeddings para ARIA attention-based memory (DEBT-048)
  · Modelo voyage-3-large · output_dimension=1024 (matchea vector(1024))
  · input_type "document" (storage) | "query" (retrieval)
  · DEPLOY-SAFE: sin VOYAGE_API_KEY o sin SDK → adapter no disponible

voyageai se importa LAZY (no instalado en venv local · runtime deploy-only).
embed_texts() retorna None en CUALQUIER fallo — los callers caen a fallback.
"""

from __future__ import annotations

import logging

from app.config import settings
from app.bc_cognition.infrastructure.hermes_usage import record_mcp_use  # HERMES f1.5 · usage-tracking

logger = logging.getLogger(__name__)

_MODEL = "voyage-3-large"
_DIMENSION = 1024
_adapter: VoyageAdapter | None = None


class VoyageAdapter:
    """Wrapper del cliente voyageai · import lazy en __init__ (SDK deploy-only)."""

    def __init__(self) -> None:
        if not settings.voyage_api_key:
            raise RuntimeError("VOYAGE_API_KEY no configurada")
        import voyageai  # noqa: I1 exc 3 — único import permitido del SDK

        self._client = voyageai.Client(api_key=settings.voyage_api_key)

    def embed(self, texts: list[str], input_type: str) -> list[list[float]]:
        """Embebe texts. input_type ∈ {document, query}. Puede lanzar (caller captura)."""
        result = self._client.embed(
            texts, model=_MODEL, input_type=input_type, output_dimension=_DIMENSION,
        )
        return [list(vec) for vec in result.embeddings]


def get_voyage_adapter() -> VoyageAdapter | None:
    """Singleton lazy. None si key ausente o SDK no instalado (deploy-safe)."""
    global _adapter
    if _adapter is None:
        try:
            _adapter = VoyageAdapter()
        except Exception as e:
            logger.warning(f"voyage_adapter unavailable: {e}")
            return None
    return _adapter


def embed_texts(texts: list[str], input_type: str) -> list[list[float]] | None:
    """Embebe texts best-effort. None ante CUALQUIER fallo (no key, SDK, API)."""
    adapter = get_voyage_adapter()
    if adapter is None:
        return None
    try:
        vecs = adapter.embed(texts, input_type)
        record_mcp_use("voyage", ok=True)  # HERMES f1.5
        return vecs
    except Exception as e:
        record_mcp_use("voyage", ok=False, detail=str(e)[:80])  # HERMES f1.5
        logger.warning(f"voyage_adapter.embed_texts failed: {e}")
        return None
