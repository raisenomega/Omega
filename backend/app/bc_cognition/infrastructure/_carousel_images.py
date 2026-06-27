"""Pieza 1 · A2.2 · genera N placas de un carrusel EN PARALELO con TODO-O-NADA (D4).

gather full (K=6 sin semáforo · rate limit MEDIDO en vivo: 0 429, wall-clock 10.1s, SDK 2.6.0).
return_exceptions=False: si UNA placa falla → propaga → 0 URLs (cero parcial · P1). El retry del
adapter (MAX_ATTEMPTS) es la red de seguridad para el 429 raro.

NO persiste (eso es A2.4) · NO inyecta marca (los prompts llegan YA enriquecidos vía fetch_brand_block,
igual que generate_images_compat). Reusa _generate_one de _image_compat (cuerpo por-placa ÚNICO · A3 intacto).
Módulo aparte de _image_compat por el techo C4 (aquél quedó en 98/100 tras extraer _generate_one).
"""
import asyncio
from typing import List, Optional

from app.bc_cognition.infrastructure._image_compat import (
    _generate_one, _SIZE_TO_ASPECT, _QUALITY_TO_ROUTE, _DEFAULT_ASPECT, _DEFAULT_ROUTE,
)


async def generate_carousel_images(
    prompts: List[str],
    client_id: Optional[str] = None,
    size: str = "1024x1280",  # 4:5 feed IG vertical (A7) · default del carrusel
    quality: str = "standard",
    reference_images_b64: Optional[List[str]] = None,
) -> List[str]:
    """N prompts (YA enriquecidos) → N URLs EN PARALELO, EN ORDEN. Todo-o-nada: 1 falla → propaga, 0 parcial.
    gather preserva el orden de entrada (urls[i] = prompts[i]) sin importar el orden de completado."""
    aspect_ratio = _SIZE_TO_ASPECT.get(size, _DEFAULT_ASPECT)
    route = _QUALITY_TO_ROUTE.get(quality, _DEFAULT_ROUTE)
    tasks = [_generate_one(p, route, reference_images_b64, aspect_ratio, client_id) for p in prompts]
    urls = await asyncio.gather(*tasks, return_exceptions=False)  # 1ª excepción propaga → todo-o-nada (D4)
    return list(urls)
