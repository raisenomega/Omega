"""Logo fetcher for ARIA multimodal (DEBT-084 · base64 fix).

El bucket brand-files es PRIVADO → pasar la storage_url pública directa a
Claude daba 400 (Anthropic no puede descargarla). Fix: descargamos el objeto
con el service-role key (supabase storage) y lo mandamos como bloque image
base64. Todo el I/O vive acá (DDD A2 — infra; domain queda puro).

Best-effort: cualquier fallo/ausencia → None (ARIA degrada a texto-only · no
rompe la conversación). La descarga sync corre en asyncio.to_thread (DEBT-074:
no bloquea el event loop).
"""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Optional

from app.infrastructure.supabase_service import get_supabase_service

_BUCKET = "brand-files"
_MAX_LOGO_BYTES: int = 5 * 1024 * 1024   # 5 MB guard
_MIME_BY_EXT = {
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "webp": "image/webp", "gif": "image/gif",
}

logger = logging.getLogger(__name__)


def _storage_path_from_url(logo_url: str) -> Optional[str]:
    """Extrae el object path dentro del bucket desde la storage_url pública."""
    marker = f"/{_BUCKET}/"
    idx = logo_url.find(marker)
    if idx == -1:
        return None
    path = logo_url[idx + len(marker):].split("?")[0]
    return path or None


def _mime_for(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower() if "." in path else ""
    return _MIME_BY_EXT.get(ext, "image/jpeg")


def _download_b64(path: str) -> Optional[tuple[str, str]]:
    """Descarga (service role) + base64. Retorna (b64, mime) o None. Sync · va en to_thread."""
    data = get_supabase_service().client.storage.from_(_BUCKET).download(path)
    if not data or len(data) > _MAX_LOGO_BYTES:
        return None
    return base64.b64encode(data).decode("ascii"), _mime_for(path)


async def fetch_logo_for_aria(logo_url: Optional[str]) -> Optional[dict]:
    """Bloque image base64 del logo del cliente (best-effort · None si falla/ausente).

    Returned dict shape (Anthropic base64 source):
        {"type": "image", "source": {"type": "base64",
         "media_type": "image/...", "data": "<b64>"}}
    """
    if not logo_url:
        return None
    path = _storage_path_from_url(logo_url)
    if not path:
        return None
    try:
        result = await asyncio.to_thread(_download_b64, path)
    except Exception as exc:
        logger.warning("fetch_logo_for_aria failed for %s: %s", path, exc)
        return None
    if not result:
        return None
    b64, mime = result
    return {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}}
