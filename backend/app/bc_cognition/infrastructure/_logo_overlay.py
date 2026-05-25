"""Overlay del logo del cliente en imágenes generadas (Fase 1 · opt-in apply_logo).

Descarga la imagen generada + el logo, superpone el logo en la esquina inferior derecha
(10% del ancho · padding 20px · opacidad 80%) con Pillow y devuelve bytes PNG. El caller
(handler) lo usa best-effort: si lanza, cae a la imagen original sin marca.
"""
import io
import httpx
from PIL import Image

_LOGO_WIDTH_RATIO = 0.10
_PADDING = 20
_OPACITY = 0.80
_TIMEOUT = 20.0


def _fetch(url: str) -> bytes:
    # follow_redirects=False · las URLs públicas de Supabase Storage son directas (no 3xx);
    # bloquea el vector SSRF-vía-redirect (defensa en profundidad · guardian rec).
    r = httpx.get(url, timeout=_TIMEOUT, follow_redirects=False)
    r.raise_for_status()
    return r.content


def overlay_logo(image_url: str, logo_url: str) -> bytes:
    """PNG bytes de la imagen con el logo superpuesto (esquina inf-derecha · 10% · 80% opac)."""
    base = Image.open(io.BytesIO(_fetch(image_url))).convert("RGBA")
    logo = Image.open(io.BytesIO(_fetch(logo_url))).convert("RGBA")
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
