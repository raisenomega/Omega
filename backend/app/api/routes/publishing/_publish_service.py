"""Service · auto-publicación real de un scheduled_post YA aprobado.

Flujo (best-effort · cero fabricación):
  1. Carga el post + valida ownership (client) + status publicable.
  2. Lee el token Meta del cliente (RONDA D). Sin token → meta_not_connected.
  3. POST real a Meta Graph (vía _meta_publisher).
  4. Éxito  → status='published' + platform_post_id.
     Fallo  → status='failed' + error_message honesto. JAMÁS finge éxito.

SAFETY (P2/P3/P4): NO genera ni aprueba contenido. El único estado publicable es
'pending' (el humano ya lo programó/aprobó desde el calendario). Cualquier otro
status → PublishGateError (el handler responde 409 honesto).
"""
import asyncio
import logging
from typing import NamedTuple, Optional

from app.api.routes.oauth._oauth_token_repository import get_token
from app.api.routes.publishing import _publish_repository as repo
from app.api.routes.publishing._meta_publisher import MetaPublishError, publish_to_meta

logger = logging.getLogger(__name__)

# Único estado desde el que se permite ejecutar la publicación real:
# 'pending' = post programado y aprobado por el humano en el calendario.
# (publishing/published/failed/published_manual/cancelled NO se re-publican.)
_PUBLISHABLE_STATUS = "pending"


class PublishGateError(Exception):
    """Violación de un gate de seguridad/precondición · el handler mapea a 4xx honesto.

    code ∈ {post_not_found, post_access_denied, post_not_publishable:<status>,
            meta_not_connected, meta_no_page}.
    """

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class PublishResult(NamedTuple):
    published: bool
    platform_post_id: Optional[str] = None
    error: Optional[str] = None


async def publish_scheduled_post(scheduled_post_id: str, client_id: str) -> PublishResult:
    """Publica de verdad un post aprobado. Raise PublishGateError en precondición
    fallida · devuelve PublishResult(published=False, error=...) si Meta rechaza."""
    post = await asyncio.to_thread(repo.get_scheduled_post, scheduled_post_id)
    if not post:
        raise PublishGateError("post_not_found")
    if str(post.get("client_id") or "") != client_id:
        raise PublishGateError("post_access_denied")

    status = str(post.get("status") or "")
    if status != _PUBLISHABLE_STATUS:
        # Cero fabricación: no re-publica algo ya publicado/cancelado/fallido.
        raise PublishGateError(f"post_not_publishable:{status}")

    token = await get_token(client_id, "meta")
    if not token or not token.get("access_token"):
        # Cero fabricación: sin token NO se finge publicación. Honesto + accionable.
        raise PublishGateError("meta_not_connected")
    page_id = token.get("external_account_id")
    if not page_id:
        raise PublishGateError("meta_no_page")

    content_id = post.get("content_id")
    message = ""
    if content_id:
        message = await asyncio.to_thread(repo.get_content_text, str(content_id))
    media_url = post.get("media_url")

    await asyncio.to_thread(repo.mark_publishing, scheduled_post_id)
    try:
        platform_post_id = await publish_to_meta(
            page_id=str(page_id),
            access_token=str(token["access_token"]),
            message=message,
            media_url=str(media_url) if media_url else None,
        )
    except MetaPublishError as e:
        error = str(e)
        logger.warning(f"auto-publish failed · post={scheduled_post_id} client={client_id} · {error}")
        await asyncio.to_thread(repo.mark_failed, scheduled_post_id, error)
        return PublishResult(published=False, error=error)
    except Exception as e:  # noqa: BLE001 · cualquier fallo inesperado → honesto, nunca finge éxito
        error = f"unexpected:{type(e).__name__}"
        logger.error(f"auto-publish unexpected · post={scheduled_post_id} · {e}", exc_info=True)
        await asyncio.to_thread(repo.mark_failed, scheduled_post_id, error)
        return PublishResult(published=False, error=error)

    await asyncio.to_thread(repo.mark_published, scheduled_post_id, platform_post_id)
    logger.info(f"auto-publish OK · post={scheduled_post_id} client={client_id} platform_post_id={platform_post_id}")
    return PublishResult(published=True, platform_post_id=platform_post_id)
