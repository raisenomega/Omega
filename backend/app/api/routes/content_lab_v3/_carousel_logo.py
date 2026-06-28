"""Commit A · overlay opt-in del logo del cliente sobre las N placas del carrusel · POST-generación
(paridad con imagen suelta · generate_image.py). Reusa overlay_logo + upload_image_bytes (NO los toca).

Best-effort POR placa: si el overlay/reupload de una falla, esa queda con su url original (sin logo) y
las demás overlaid · el carrusel NUNCA se cae por el logo (la generación ya pasó · esto es post). En
paralelo (asyncio.gather) · overlay_logo/upload son sync+IO → to_thread (no bloquea el event loop)."""
import asyncio
import logging

from app.bc_cognition.infrastructure._logo_overlay import overlay_logo
from app.bc_cognition.infrastructure._storage_uploader import upload_image_bytes

logger = logging.getLogger(__name__)


async def _overlay_one(url: str, logo_url: str, client_id: str) -> str:
    """1 placa con logo · best-effort: si overlay/reupload falla → la url original (sin logo, no rompe)."""
    try:
        overlaid = await asyncio.to_thread(overlay_logo, url, logo_url)
        return await upload_image_bytes(overlaid, "image/png", client_id)
    except Exception as e:  # noqa: BLE001 · best-effort · esa placa sin logo, no tumba el carrusel
        logger.warning(f"logo overlay falló · placa sin marca · client={client_id} url={url}: {e}")
        return url


async def apply_logo_to_urls(urls: list[str], logo_url: str, client_id: str) -> list[str]:
    """Overlay del logo sobre las N placas EN PARALELO · best-effort por placa · preserva el orden
    (gather respeta el orden de entrada). logo_url ya resuelto (el caller verifica que no sea None)."""
    return list(await asyncio.gather(*[_overlay_one(u, logo_url, client_id) for u in urls]))
