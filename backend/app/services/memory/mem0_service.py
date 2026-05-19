"""
Servicio de memoria persistente con mem0 — STUB inerte.
DEBT-012: mem0ai comentado en requirements.txt por conflicto sqlalchemy.
Stub mantiene API pública (`omega_memory`, `MemoryService`) con
graceful degradation: `remember` no-op, `recall`/`search` retornan vacío.
Restauración: descomentar mem0ai en requirements.txt + revertir este file.
"""
from typing import Optional
import logging

from app.domain.memory.types import (
    MemoryMetadata, MemorySearchResponse,
)

logger = logging.getLogger(__name__)


class _InertMemory:
    """Stub no-op de mem0.Memory — preserva la API esperada por callers."""

    def add(self, *_args: object, **_kwargs: object) -> None:
        logger.debug("mem0.add skipped · DEBT-012")

    def search(self, *_args: object, **_kwargs: object) -> dict:
        logger.debug("mem0.search returns empty · DEBT-012")
        return {"results": []}

    def get_all(self, *_args: object, **_kwargs: object) -> list:
        logger.debug("mem0.get_all returns empty · DEBT-012")
        return []


# Instancia global inerte
omega_memory = _InertMemory()


class MemoryService:
    """Servicio de memoria — stub graceful degradation · DEBT-012."""

    @staticmethod
    async def remember(
        client_id: str,
        interaction: str,
        metadata: Optional[MemoryMetadata] = None
    ) -> None:
        """No-op · DEBT-012 — mem0 disabled."""
        logger.debug(f"MemoryService.remember skipped for {client_id} · DEBT-012")

    @staticmethod
    async def recall(
        client_id: str,
        query: str,
        limit: int = 5
    ) -> str:
        """Retorna string vacío · DEBT-012 — mem0 disabled."""
        return ""

    @staticmethod
    async def search(
        client_id: str,
        query: str,
        limit: int = 10
    ) -> MemorySearchResponse:
        """Retorna response vacío · DEBT-012 — mem0 disabled."""
        return MemorySearchResponse(results=[], total=0)

    @staticmethod
    async def get_all(client_id: str) -> list[dict]:
        """Retorna lista vacía · DEBT-012 — mem0 disabled."""
        return []
