"""Guard de aspect ratio per-plataforma al publicar (P1 honest failure · evita el zernio_400 enganoso).

AUTORIDAD del rango = la plataforma destino, NO Zernio. Instagram FEED acepta ratio (w/h) de 0.8
(4:5 vertical) a 1.91 (landscape) — documentado por Instagram. Una imagen 9:16 (0.5625) la rechaza,
y Zernio devuelve el enganoso "requires media content". Aca lo cazamos antes y fallamos honesto.

FUENTE UNICA DEL RANGO: _FEED_RATIO_RULES. DEBE coincidir con el aviso inline del frontend
(src/lib/feed-aspect.ts · mismos numeros, misma fuente). Si divergen, el aviso no calza con el rechazo.

tiktok / facebook / linkedin / twitter = lenientes (vertical OK · sin tope aca). El routing de
verticales a Reel/Story (para que el 9:16 publique bien en vez de solo fallar) es DEBT-PLACEMENT (aparte).

Como obtenemos el ratio: metadata del contenido NO guarda aspect_ratio de forma confiable
(solo model/provider/style/ui_type), asi que leemos las dimensiones del HEADER de la imagen.
Fail-open: si no se puede medir (fetch falla / formato raro) -> None -> NO bloquea (no matamos un
post por no poder medirlo).
"""
from typing import Optional
import logging
import httpx

logger = logging.getLogger(__name__)

# (min, max) de ratio w/h por red con feed acotado. Fuente: Instagram feed. Sincronizado con frontend.
_FEED_RATIO_RULES: dict[str, tuple[float, float]] = {
    "instagram": (0.8, 1.91),
}


def needs_ratio_check(platform: str) -> bool:
    """True solo si la red tiene rango de feed acotado (evita fetch innecesario en tiktok/fb/etc)."""
    return platform in _FEED_RATIO_RULES


def aspect_error(platform: str, ratio: float) -> Optional[str]:
    """Codigo de error honesto si el ratio NO sirve para el feed de la red · None si OK (o red leniente).
    ratio = width/height. IG feed exige [0.8, 1.91]; vertical 9:16 (0.5625) -> rechazo de esa fila."""
    rng = _FEED_RATIO_RULES.get(platform)
    if rng is not None and not (rng[0] <= ratio <= rng[1]):
        return f"imagen_vertical_no_apta_feed_ig:{ratio:.2f}"
    return None


async def fetch_image_ratio(url: str) -> Optional[float]:
    """ratio w/h leido del header de la imagen · None si no se pudo (fail-open: no bloquea el publish)."""
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as c:
            resp = await c.get(url)
        if resp.status_code != 200:
            return None
        from io import BytesIO
        from PIL import Image
        with Image.open(BytesIO(resp.content)) as im:
            w, h = im.size
        return (w / h) if h else None
    except Exception as e:  # noqa: BLE001 · fail-open: si no podemos medir, no matamos el post
        logger.warning(f"aspect guard · no se pudo leer ratio de la imagen: {type(e).__name__}")
        return None
