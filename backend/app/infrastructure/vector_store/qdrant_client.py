"""
Cliente de Qdrant para vector store.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.domain.memory.types import QDRANT_CONFIG
from app.core.config import settings

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Cliente singleton de Qdrant."""

    _instance: Optional[QdrantClient] = None
    _initialized: bool = False

    @classmethod
    def get_client(cls) -> QdrantClient:
        """
        Obtiene instancia singleton del cliente Qdrant.

        Returns:
            QdrantClient conectado
        """
        if cls._instance is None:
            cls._instance = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            logger.info(
                f"Qdrant client initialized: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}"
            )

        return cls._instance

    @classmethod
    def ensure_collection(cls) -> None:
        """
        Asegura que la colección de memorias exista.

        Crea la colección si no existe.
        Idempotente - safe llamar múltiples veces.
        """
        if cls._initialized:
            return

        client = cls.get_client()
        collection_name = QDRANT_CONFIG["collection_name"]

        try:
            # Verificar si existe
            collections = client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if not exists:
                # Crear colección
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=QDRANT_CONFIG["vector_size"],
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {collection_name}")
            else:
                logger.info(f"Qdrant collection exists: {collection_name}")

            cls._initialized = True

        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")
            raise

    @classmethod
    def health_check(cls) -> bool:
        """
        Verifica que Qdrant esté accesible.

        Returns:
            True si Qdrant responde, False si no
        """
        try:
            client = cls.get_client()
            client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Función helper para inicialización en startup
async def initialize_qdrant() -> None:
    """
    Inicializa Qdrant en el startup de la app.

    Llamar desde main.py en @app.on_event("startup")
    """
    try:
        QdrantVectorStore.ensure_collection()
        logger.info("Qdrant initialized successfully")
    except Exception as e:
        logger.error(f"Qdrant initialization failed: {e}")
        # No raise - permitir que la app arranque sin memoria
