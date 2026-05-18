"""
Handler para guardar/favorito contenido.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.content_lab.models import SaveContentResponse
from app.infrastructure.repositories.content_lab_repository import (
    ContentLabRepository
)

logger = logging.getLogger(__name__)


async def handle_save_content(content_id: str) -> SaveContentResponse:
    """
    Handler para toggle estado de guardado (favorito).

    Invierte el estado actual de is_saved del contenido.

    Args:
        content_id: UUID del contenido

    Returns:
        SaveContentResponse con ID y nuevo estado

    Raises:
        HTTPException 404: Contenido no encontrado
        HTTPException 500: Error en actualización
    """
    try:
        repo = ContentLabRepository()

        # 1. Obtener contenido actual
        entity = repo.get_by_id(content_id)

        if not entity:
            raise HTTPException(404, f"Contenido {content_id} no encontrado")

        # 2. Toggle saved status usando lógica de dominio
        entity.toggle_saved()

        # 3. Persistir cambio
        updated_entity = repo.update_saved_status(
            content_id=content_id,
            is_saved=entity.is_saved
        )

        if not updated_entity:
            raise HTTPException(500, "Error actualizando estado")

        logger.info(
            f"Toggled saved status for content {content_id}: "
            f"{updated_entity.is_saved}"
        )

        return SaveContentResponse(
            id=content_id,
            saved=updated_entity.is_saved
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save content failed: {e}")
        raise HTTPException(500, f"Error guardando contenido: {str(e)}")
