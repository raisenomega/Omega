"""
Servicio de memoria persistente con mem0.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
import logging
from mem0 import Memory

from app.domain.memory.types import (
    MemoryMetadata, MemoryEntry, MemorySearchResponse,
    MemorySearchResult, MEM0_CONFIG
)
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configuración de mem0
memory_config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": settings.QDRANT_HOST,
            "port": settings.QDRANT_PORT,
            "collection_name": MEM0_CONFIG["collection_name"],
        }
    },
    "llm": {
        "provider": "litellm",
        "config": {
            "model": MEM0_CONFIG["llm_model"]
        }
    },
    "version": MEM0_CONFIG["version"]
}

# Instancia global de mem0
omega_memory = Memory.from_config(memory_config)


class MemoryService:
    """Servicio de gestión de memoria persistente."""

    @staticmethod
    async def remember(
        client_id: str,
        interaction: str,
        metadata: Optional[MemoryMetadata] = None
    ) -> None:
        """
        Guarda una interacción en memoria.

        Args:
            client_id: ID del cliente (será prefijado con 'client_')
            interaction: Texto de la interacción
            metadata: Metadata opcional

        Note:
            Si falla, no lanza excepción - graceful degradation
        """
        try:
            user_id = f"client_{client_id}"

            # Preparar metadata
            meta_dict = {}
            if metadata:
                meta_dict = metadata.model_dump(exclude_none=True)

            # Guardar en mem0
            omega_memory.add(
                messages=[{"role": "user", "content": interaction}],
                user_id=user_id,
                metadata={
                    "source": "omega",
                    "type": "client_interaction",
                    **meta_dict
                }
            )

            logger.info(f"Memory saved for client {client_id}")

        except Exception as e:
            logger.error(f"Memory save failed for {client_id}: {e}")
            # No raise - memoria es enhancement, no crítico

    @staticmethod
    async def recall(
        client_id: str,
        query: str,
        limit: int = 5
    ) -> str:
        """
        Recupera memorias relevantes.

        Args:
            client_id: ID del cliente
            query: Query de búsqueda
            limit: Máximo de memorias a retornar

        Returns:
            Contexto formateado para inyectar en system prompt

        Note:
            Si falla, retorna string vacío - graceful degradation
        """
        try:
            user_id = f"client_{client_id}"

            results = omega_memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )

            if not results.get("results"):
                return ""

            memories = [r["memory"] for r in results["results"]]

            formatted = (
                "CONTEXTO DEL CLIENTE (de interacciones previas):\n" +
                "\n".join(f"• {m}" for m in memories)
            )

            logger.info(
                f"Recalled {len(memories)} memories for client {client_id}"
            )

            return formatted

        except Exception as e:
            logger.error(f"Memory recall failed for {client_id}: {e}")
            return ""  # Graceful degradation

    @staticmethod
    async def search(
        client_id: str,
        query: str,
        limit: int = 10
    ) -> MemorySearchResponse:
        """
        Búsqueda detallada de memorias.

        Args:
            client_id: ID del cliente
            query: Query de búsqueda
            limit: Máximo de resultados

        Returns:
            MemorySearchResponse con resultados y metadata
        """
        try:
            user_id = f"client_{client_id}"

            results = omega_memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )

            search_results = []
            for r in results.get("results", []):
                search_results.append(
                    MemorySearchResult(
                        memory=r["memory"],
                        score=r.get("score", 0.0),
                        metadata=r.get("metadata", {})
                    )
                )

            return MemorySearchResponse(
                results=search_results,
                total=len(search_results)
            )

        except Exception as e:
            logger.error(f"Memory search failed for {client_id}: {e}")
            return MemorySearchResponse(results=[], total=0)

    @staticmethod
    async def get_all(client_id: str) -> list[dict]:
        """
        Obtiene todas las memorias de un cliente.

        Args:
            client_id: ID del cliente

        Returns:
            Lista de todas las memorias

        Note:
            Para debugging/admin - no usar en producción
        """
        try:
            user_id = f"client_{client_id}"
            return omega_memory.get_all(user_id=user_id)
        except Exception as e:
            logger.error(f"Get all memories failed for {client_id}: {e}")
            return []
