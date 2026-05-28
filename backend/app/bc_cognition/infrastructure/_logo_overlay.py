"""Overlay del logo del cliente en imágenes generadas (DEBT-FFMPEG · opt-in apply_logo).

Imagen generada: bucket público `generated-images` → httpx.get directo.
Logo: bucket PRIVADO `brand-files` → service-role storage download (la URL pública
/object/public/ devuelve 404 "Bucket not found"; mismo patrón que _logo_fetcher).
Superpone el logo en la esquina inf-derecha (15% width · 20px padding · 80% opac) con
Pillow y devuelve bytes PNG. Best-effort: si lanza, caller cae a imagen sin marca.
"""
import io
import logging
from typing import Optional

import httpx
from PIL import Image

from app.infrastructure.supabase_service import get_supabase_service

_LOGO_WIDTH_RATIO = 0.15
_PADDING = 20
_OPACITY = 0.80
_TIMEOUT = 20.0
_BUCKET = "brand-files"
_MAX_LOGO_BYTES = 5 * 1024 * 1024  # 5 MB guard (mismo límite que _logo_fetcher)

logger = logging.getLogger(__name__)


def _fetch_image(url: str) -> bytes:
    """HTTP GET de la imagen generada (bucket público generated-images). follow_redirects=False · SSRF defense."""
    r = httpx.get(url, timeout=_TIMEOUT, follow_redirects=False)
    r.raise_for_status()
    return r.content


def _storage_path_from_url(logo_url: str) -> Optional[str]:
    """Extrae el object path dentro de brand-files desde la storage_url."""
    marker = f"/{_BUCKET}/"
    idx = logo_url.find(marker)
    if idx == -1:
        return None
    path = logo_url[idx + len(marker):].split("?")[0]
    return path or None


def download_logo_bytes(logo_url: str) -> Optional[bytes]:
    """Descarga el logo del bucket PRIVADO via service-role · None si fallo o ausencia."""
    path = _storage_path_from_url(logo_url)
    if not path:
        return None
    try:
        data = get_supabase_service().client.storage.from_(_BUCKET).download(path)
    except Exception as exc:
        logger.warning("download_logo_bytes failed for %s: %s", path, exc)
        return None
    if not data or len(data) > _MAX_LOGO_BYTES:
        return None
    return data


def overlay_logo(image_url: str, logo_url: str) -> bytes:
    """PNG bytes de la imagen con el logo superpuesto (esquina inf-derecha · 15% · 80% opac)."""
    base = Image.open(io.BytesIO(_fetch_image(image_url))).convert("RGBA")
    logo_bytes = download_logo_bytes(logo_url)
    if not logo_bytes:
        raise ValueError(f"logo no descargable desde {logo_url}")
    logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
    if logo.width == 0 or logo.height == 0:
        raise ValueError("logo vacío (dimensiones 0)")
    target_w = max(1, int(base.width * _LOGO_WIDTH_RATIO))
    target_h = max(1, round(logo.height * target_w / logo.width))
    logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
    alpha = logo.getchannel("A").point(lambda a: round(a * _OPACITY))
    logo.putalpha(alpha)
    pos = (base.width - target_w - _PADDING, base.height - target_h - _PADDING)
    base.alpha_composite(logo, pos)
    out = io.BytesIO()
    base.convert("RGB").save(out, format="PNG")
    return out.getvalue()
