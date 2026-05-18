"""
Handler para listar contenido generado.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.content_lab.models import ContentListResponse
from app.infrastructure.repositories.content_lab_repository import (
    ContentLabRepository
)

logger = logging.getLogger(__name__)


async def handle_list_content(
    client_id: str,
    content_type: str | None,
    limit: int,
    offset: int
) -> ContentListResponse:
    """
    Handler para listar contenido generado de un cliente.

    Args:
        client_id: UUID del cliente
        content_type: Filtro opcional por tipo
        limit: Máximo de resultados
        offset: Offset para paginación

    Returns:
        ContentListResponse con items y total

    Raises:
        HTTPException 500: Error en consulta
    """
    try:
        repo = ContentLabRepository()

        # Obtener contenido desde repository
        entities, total = repo.list_by_client(
            client_id=client_id,
            content_type=content_type,
            limit=limit,
            offset=offset
        )

        # Convertir entidades a dicts
        items = [entity.to_dict() for entity in entities]

        logger.info(
            f"Listed {len(items)} content items for client {client_id}"
        )

        return ContentListResponse(items=items, total=total)

    except Exception as e:
        logger.error(f"List content failed: {e}")
        raise HTTPException(500, f"Error listando contenido: {str(e)}")
