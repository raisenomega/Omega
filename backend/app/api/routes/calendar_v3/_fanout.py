"""E · fan-out multi-red del bloque Content Lab (funcion pura · espeja maybe_schedule_on_approve).

Producto cruzado: N items de texto (content_ids · timestamps espaciados) x M redes marcadas resueltas
-> 1 row por (red, item). Cada red comparte el mismo set de N timestamps (mismo cronograma por red).
INVARIANTE (cierra sin_red de raiz): red sin cuenta active -> OMITIDA · jamas social_account_id NULL.
Si ninguna red resuelve -> [] (el handler lo convierte en 422 · error claro · 0 rows basura).
"""
from datetime import datetime
from typing import Any, Callable, Optional

from app.api.routes.calendar_v3._access import first_active_account_id_or_none


def normalize_platforms(raw: Optional[list[str]]) -> list[str]:
    """Redes marcadas -> lowercase (casa social_accounts.platform) + strip + dedup, dropea ''/'general'
    (calca _supervised_approve._target_platforms)."""
    plats = [str(p).strip().lower() for p in (raw or []) if str(p).strip()]
    seen: set[str] = set()
    return [p for p in plats if p != "general" and not (p in seen or seen.add(p))]


def build_fanout_rows(
    client_id: str,
    platforms: Optional[list[str]],
    content_ids: list[str],
    timestamps: list[datetime],
    media_url: Optional[str],
    resolve: Callable[[str, str], Optional[str]] = first_active_account_id_or_none,
    is_story: bool = False,
) -> list[dict[str, Any]]:
    """1 row por (red resuelta, content_id). resolve inyectable (tests). [] si ninguna red resuelve.
    is_story (Pieza 3) viaja en cada fila · el filtro por-red (story solo IG/FB) lo aplica REX al publicar."""
    rows: list[dict[str, Any]] = []
    for platform in normalize_platforms(platforms):
        account_id = resolve(client_id, platform)
        if not account_id:
            continue  # red sin cuenta active -> omitida (jamas social_account_id NULL)
        for cid, ts in zip(content_ids, timestamps):
            rows.append({
                "client_id": client_id,
                "social_account_id": account_id,
                "content_id": cid,
                "scheduled_for": ts.isoformat(),
                "status": "pending",
                "media_url": media_url,
                "is_story": is_story,
            })
    return rows
