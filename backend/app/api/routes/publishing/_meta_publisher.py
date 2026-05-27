"""Llamada real a Meta Graph para publicar en una Page de Facebook (RONDA D token).

Cero fabricación: si Graph no devuelve 200 + id, se levanta MetaPublishError con el
detalle honesto de Meta (el service lo persiste en error_message · NUNCA finge éxito).

- Con media_url  → POST /{page_id}/photos     (url + caption=message + published=true)
- Sin media_url  → POST /{page_id}/feed        (message [+ link])
Devuelve el id del post/foto creado en la plataforma (platform_post_id).
"""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_GRAPH_VERSION = "v21.0"
_GRAPH_BASE = f"https://graph.facebook.com/{_GRAPH_VERSION}"
_HTTP_TIMEOUT = 20.0


class MetaPublishError(Exception):
    """Fallo honesto de la publicación en Meta · mensaje apto para error_message."""


def _extract_post_id(payload: dict[str, object]) -> Optional[str]:
    """Meta devuelve {id} en /feed y {id, post_id} en /photos. Prioriza post_id."""
    post_id = payload.get("post_id") or payload.get("id")
    return str(post_id) if post_id else None


async def publish_to_meta(
    page_id: str,
    access_token: str,
    message: str,
    media_url: Optional[str] = None,
    link: Optional[str] = None,
) -> str:
    """Publica de verdad en la Page de Meta. Devuelve el platform_post_id real.

    Raise MetaPublishError con el detalle de Graph si la API no confirma el éxito.
    """
    if media_url:
        endpoint = f"{_GRAPH_BASE}/{page_id}/photos"
        data: dict[str, str] = {
            "url": media_url,
            "caption": message,
            "published": "true",
            "access_token": access_token,
        }
    else:
        endpoint = f"{_GRAPH_BASE}/{page_id}/feed"
        data = {"message": message, "access_token": access_token}
        if link:
            data["link"] = link

    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.post(endpoint, data=data)
    except httpx.HTTPError as e:
        logger.warning(f"meta publish transport error · page={page_id} · {e}")
        raise MetaPublishError(f"meta_transport_error:{type(e).__name__}") from e

    if resp.status_code != 200:
        logger.warning(f"meta publish failed · page={page_id} · {resp.status_code} · {resp.text[:300]}")
        raise MetaPublishError(f"meta_graph_{resp.status_code}:{resp.text[:200]}")

    platform_post_id = _extract_post_id(resp.json())
    if not platform_post_id:
        logger.warning(f"meta publish no id · page={page_id} · {resp.text[:200]}")
        raise MetaPublishError("meta_no_post_id")
    return platform_post_id
