"""
Cliente de Qdrant para vector store — STUB inerte.
DEBT-012: qdrant-client comentado en requirements.txt por conflicto con
sqlalchemy 2.0.25 (mem0ai exige >=2.0.31). Stub mantiene API pública
para que main.py y futuros callers importen sin crash.
Restauración: descomentar qdrant-client en requirements.txt + revertir este file.
"""
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Stub inerte de Qdrant — todos los métodos loguean y no-op."""

    _instance: Optional[object] = None
    _initialized: bool = False

    @classmethod
    def get_client(cls) -> None:
        logger.warning("QdrantVectorStore.get_client called but Qdrant disabled · DEBT-012")
        return None

    @classmethod
    def ensure_collection(cls) -> None:
        logger.warning("QdrantVectorStore.ensure_collection skipped · DEBT-012")
        return None

    @classmethod
    def health_check(cls) -> bool:
        logger.warning("QdrantVectorStore.health_check returns False · DEBT-012")
        return False


async def initialize_qdrant() -> None:
    """Stub de inicialización — no-op."""
    logger.warning("initialize_qdrant skipped · Qdrant disabled · DEBT-012")
