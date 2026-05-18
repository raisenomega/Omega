"""
Content Lab Repository
Capa de infraestructura para acceso a datos de contenido generado
Filosofía: No velocity, only precision 🐢💎
"""
from typing import List, Optional
from datetime import datetime
import logging

from app.domain.content_lab.entities import ContentLabGenerated
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class ContentLabRepository:
    """
    Repository para operaciones CRUD de contenido generado.

    Implementa patrón Repository para abstraer acceso a datos.
    """

    def __init__(self):
        self.supabase = get_supabase_service()
        self.table = "content_lab_generated"

    def list_by_client(
        self,
        client_id: str,
        content_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[ContentLabGenerated], int]:
        """
        Lista contenido generado para un cliente con paginación.

        Args:
            client_id: UUID del cliente
            content_type: Filtro opcional por tipo
            limit: Máximo de resultados
            offset: Offset para paginación

        Returns:
            Tuple de (lista de entidades, total count)
        """
        try:
            # Build query
            query = self.supabase.client.table(self.table)\
                .select("*", count="exact")\
                .eq("client_id", client_id)\
                .order("created_at", desc=True)

            # Apply content_type filter if provided
            if content_type:
                query = query.eq("content_type", content_type)

            # Apply pagination
            query = query.range(offset, offset + limit - 1)

            response = query.execute()

            # Convert to entities
            entities = [
                self._row_to_entity(row) for row in response.data
            ]

            total = response.count or 0

            logger.info(
                f"Listed {len(entities)} content items for client {client_id} "
                f"(total: {total})"
            )

            return entities, total

        except Exception as e:
            logger.error(f"Error listing content: {e}")
            raise

    def get_by_id(self, content_id: str) -> Optional[ContentLabGenerated]:
        """
        Obtiene contenido por ID.

        Args:
            content_id: UUID del contenido

        Returns:
            Entidad o None si no existe
        """
        try:
            response = self.supabase.client.table(self.table)\
                .select("*")\
                .eq("id", content_id)\
                .execute()

            if not response.data:
                return None

            return self._row_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error getting content {content_id}: {e}")
            raise

    def update_saved_status(
        self,
        content_id: str,
        is_saved: bool
    ) -> Optional[ContentLabGenerated]:
        """
        Actualiza estado de guardado (favorito).

        Args:
            content_id: UUID del contenido
            is_saved: Nuevo estado

        Returns:
            Entidad actualizada o None si no existe
        """
        try:
            response = self.supabase.client.table(self.table)\
                .update({
                    "is_saved": is_saved,
                    "updated_at": datetime.utcnow().isoformat()
                })\
                .eq("id", content_id)\
                .execute()

            if not response.data:
                return None

            logger.info(
                f"Updated saved status for content {content_id}: {is_saved}"
            )

            return self._row_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error updating saved status: {e}")
            raise

    def soft_delete(self, content_id: str) -> bool:
        """
        Elimina contenido (hard delete - tabla no tiene soft delete).

        Args:
            content_id: UUID del contenido

        Returns:
            True si se eliminó, False si no existe
        """
        try:
            response = self.supabase.client.table(self.table)\
                .delete()\
                .eq("id", content_id)\
                .execute()

            success = len(response.data) > 0

            if success:
                logger.info(f"Deleted content {content_id}")
            else:
                logger.warning(f"Content {content_id} not found for deletion")

            return success

        except Exception as e:
            logger.error(f"Error deleting content: {e}")
            raise

    def _row_to_entity(self, row: dict) -> ContentLabGenerated:
        """
        Convierte fila de DB a entidad de dominio.

        Args:
            row: Fila de base de datos

        Returns:
            Entidad ContentLabGenerated
        """
        return ContentLabGenerated(
            id=row["id"],
            client_id=row["client_id"],
            social_account_id=row["social_account_id"],
            content_type=row["content_type"],
            content=row["content"],
            provider=row["provider"],
            model=row["model"],
            tokens_used=row.get("tokens_used", 0),
            is_saved=row.get("is_saved", False),
            created_at=datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else datetime.utcnow(),
            updated_at=datetime.fromisoformat(row["updated_at"])
            if row.get("updated_at")
            else None
        )
