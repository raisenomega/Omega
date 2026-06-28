"""E · fan-out multi-red del bloque Content Lab (funcion pura · espeja maybe_schedule_on_approve).

Producto cruzado: N items de texto (content_ids · timestamps espaciados) x M redes marcadas resueltas
-> 1 row por (red, item). Cada red comparte el mismo set de N timestamps (mismo cronograma por red).
INVARIANTE (cierra sin_red de raiz): red sin cuenta active -> OMITIDA · jamas social_account_id NULL.
Si ninguna red resuelve -> [] (el handler lo convierte en 422 · error claro · 0 rows basura).
"""
from datetime import datetime
from typing import Any, Callable, Optional

from app.api.routes.calendar_v3._access import first_active_account_id_or_none
# AMBAS · single source de las redes con historia (sin ciclo: _publish_service no importa _fanout).
from app.api.routes.publishing._publish_service import _STORY_PLATFORMS


def normalize_platforms(raw: Optional[list[str]]) -> list[str]:
    """Redes marcadas -> lowercase (casa social_accounts.platform) + strip + dedup, dropea ''/'general'
    (calca _supervised_approve._target_platforms)."""
    plats = [str(p).strip().lower() for p in (raw or []) if str(p).strip()]
    seen: set[str] = set()
    return [p for p in plats if p != "general" and not (p in seen or seen.add(p))]


def _placement_variants(placement: str, platform: str) -> list[bool]:
    """is_story a emitir por (placement, red). feed→[False] · story→[True] ·
    both→[False] + [True] SOLO si la red soporta historia (IG/FB · resto solo feed)."""
    if placement == "story":
        return [True]
    if placement == "both":
        return [False] + ([True] if platform in _STORY_PLATFORMS else [])
    return [False]  # 'feed' (default)


def rows_for_account(
    client_id: str, account_id: str, platform: str,
    content_ids: list[str], timestamps: list[datetime],
    media_url: Optional[str], placement: str,
    media_urls: Optional[list[str]] = None,
    media_content_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Filas de UNA cuenta resuelta: 1-2 variantes (feed/story) x N content_ids. Feed primero, luego
    story (mismo timestamp · son el mismo momento, dos placements). Reusado por fan-out y legacy (DRY).
    Media scopeado por pieza: media_urls (array) + media_url=array[0] (doble-escritura) se escriben SOLO
    en la fila cuyo content_id es el dueño del media (media_content_id) → las demás piezas del MISMO bloque
    (caption/etc) quedan SIN media (cierra el bleed). media_content_id=None → retrocompat (media a todas)."""
    rows: list[dict[str, Any]] = []
    for is_story in _placement_variants(placement, platform):
        for cid, ts in zip(content_ids, timestamps):
            owns = media_content_id is None or cid == media_content_id
            urls = media_urls if (owns and media_urls) else None
            single = (media_urls[0] if media_urls else media_url) if owns else None
            rows.append({
                "client_id": client_id,
                "social_account_id": account_id,
                "content_id": cid,
                "scheduled_for": ts.isoformat(),
                "status": "pending",
                "media_url": single,
                "media_urls": urls,
                "is_story": is_story,
            })
    return rows


def build_fanout_rows(
    client_id: str,
    platforms: Optional[list[str]],
    content_ids: list[str],
    timestamps: list[datetime],
    media_url: Optional[str],
    resolve: Callable[[str, str], Optional[str]] = first_active_account_id_or_none,
    placement: str = "feed",
    media_urls: Optional[list[str]] = None,
    media_content_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    """1-2 rows por (red resuelta, content_id) segun placement. resolve inyectable (tests). [] si
    ninguna red resuelve. INVARIANTE: red sin cuenta active -> omitida (jamas social_account_id NULL).
    media_content_id: la pieza dueña del media (el carrusel del bloque) · solo su fila lleva media_urls
    (las demás piezas del bloque quedan sin media · cierra el bleed)."""
    rows: list[dict[str, Any]] = []
    for platform in normalize_platforms(platforms):
        account_id = resolve(client_id, platform)
        if not account_id:
            continue  # red sin cuenta active -> omitida (ni feed ni story)
        rows.extend(rows_for_account(
            client_id, account_id, platform, content_ids, timestamps, media_url, placement,
            media_urls=media_urls, media_content_id=media_content_id))
    return rows
