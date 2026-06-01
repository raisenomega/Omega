"""Adapter Zernio · publicacion real en N plataformas bajo 1 ZERNIO_API_KEY (un perfil por cuenta).

Cero fabricacion (patron espejo de _meta_publisher.py): si Zernio no devuelve 2xx + post id,
levanta ZernioPublishError con el detalle honesto · NUNCA finge exito. Si falta la key →
ZernioNotConfigured (no publica · no inventa). Contrato verificado en vivo contra docs.zernio.com
(1 jun 2026): POST /posts {content, platforms:[{platform, accountId}], publishNow|scheduledFor,
mediaItems:[{url,type}]} → 201 {post:{_id}} · GET /accounts → {accounts:[{_id, platform, ...}]}.
"""
import logging
from typing import Optional

import httpx

from app.bc_cognition.infrastructure.zernio_config import get_zernio_settings

logger = logging.getLogger(__name__)
_HTTP_TIMEOUT = 40.0


class ZernioError(Exception):
    """Base · fallo honesto de Zernio."""


class ZernioNotConfigured(ZernioError):
    """ZERNIO_API_KEY ausente · sin publicar (regla cero-mocks · no finge conexion)."""


class ZernioPublishError(ZernioError):
    """Zernio no confirmo la operacion · mensaje apto para error_message (cero fabricacion)."""


def _conf() -> tuple[dict, str]:
    """Headers (Bearer) + base URL · raise ZernioNotConfigured si la key esta vacia."""
    s = get_zernio_settings()
    if not s.zernio_api_key.strip():
        raise ZernioNotConfigured("zernio_api_key_ausente")
    headers = {"Authorization": f"Bearer {s.zernio_api_key}", "Content-Type": "application/json"}
    return headers, s.zernio_api_base


async def list_accounts() -> list[dict]:
    """Cuentas/perfiles conectados bajo la key (GET /accounts → [{_id, platform, ...}]).
    NOTA paginacion: /accounts limita resultados; si Zernio expone cursor, manejar aca (Fase 5)."""
    headers, base = _conf()
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.get(f"{base}/accounts")
        except httpx.HTTPError as e:
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code != 200:
        raise ZernioPublishError(f"zernio_accounts_{resp.status_code}:{resp.text[:200]}")
    return resp.json().get("accounts", [])


def _media_type(url: str) -> str:
    """Infiere el type que Zernio exige en mediaItems ('image'|'video') desde la extension.
    Default 'image' (la mayoria de los posts). TikTok/video sin extension clara = limitacion conocida."""
    u = url.lower().split("?")[0]
    return "video" if u.endswith((".mp4", ".mov", ".webm", ".m4v")) else "image"


async def create_post(content: str, platforms: list[dict], publish_now: bool = True,
                      scheduled_for: Optional[str] = None,
                      media_urls: Optional[list[str]] = None) -> str:
    """Publica de verdad en Zernio. platforms = [{"platform": str, "accountId": str}].
    Devuelve el post _id real · raise ZernioPublishError si Zernio no confirma (jamas finge exito)."""
    body: dict[str, object] = {"content": content, "platforms": platforms}
    if media_urls:
        # Zernio exige mediaItems:[{url,type}] al top-level (NO mediaUrls · verificado docs.zernio.com
        # /guides/media-uploads · sin esto IG/TikTok rechazan "requires media"). type inferido por ext.
        body["mediaItems"] = [{"url": u, "type": _media_type(u)} for u in media_urls]
    if scheduled_for:
        body["scheduledFor"] = scheduled_for  # uno u otro · no ambos
    else:
        body["publishNow"] = publish_now
    headers, base = _conf()
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.post(f"{base}/posts", json=body)
        except httpx.HTTPError as e:
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code not in (200, 201):
        logger.warning(f"zernio publish failed · {resp.status_code} · {resp.text[:300]}")
        raise ZernioPublishError(f"zernio_{resp.status_code}:{resp.text[:200]}")
    post_id = (resp.json().get("post") or {}).get("_id")
    if not post_id:
        raise ZernioPublishError("zernio_no_post_id")
    return str(post_id)
