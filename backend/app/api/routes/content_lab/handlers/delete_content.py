"""
Handler para eliminar contenido (soft delete).
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.content_lab.models import DeleteContentResponse
from app.infrastructure.repositories.content_lab_repository import (
    ContentLabRepository
)

logger = logging.getLogger(__name__)


async def handle_delete_content(content_id: str) -> DeleteContentResponse:
    """
    Handler para eliminar contenido (soft delete).

    Marca el contenido como is_active=False en lugar de eliminarlo físicamente.

    Args:
        content_id: UUID del contenido

    Returns:
        DeleteContentResponse con ID y confirmación

    Raises:
        HTTPException 404: Contenido no encontrado
        HTTPException 500: Error en eliminación
    """
    try:
        repo = ContentLabRepository()

        # Soft delete en repository
        success = repo.soft_delete(content_id)

        if not success:
            raise HTTPException(404, f"Contenido {content_id} no encontrado")

        logger.info(f"Soft deleted content {content_id}")

        return DeleteContentResponse(
            id=content_id,
            deleted=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete content failed: {e}")
        raise HTTPException(500, f"Error eliminando contenido: {str(e)}")
