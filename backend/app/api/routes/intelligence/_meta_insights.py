"""Meta Graph insights helper · Centro de Inteligencia Fase 2 (chip Meta).

Lee el token OAuth del cliente (get_token · RONDA D, read-only) y consulta Graph API
con ese token. Best-effort + honesto (regla cero-mocks · CI-R1/CI-R7):
  · sin token        → {"state": "not_connected", ...}  (jamás fabrica números)
  · Graph falla/vacío → {"state": "error"/"empty", ...}  (nunca levanta · nunca 500)
  · ok               → {"state": "ok", "metrics": {followers, engagement, reach}}

NO escribe nada. NO toca oauth/. external_account_id = page id (de /me/accounts en el connect).
"""
import logging
from typing import Optional

import httpx

from app.api.routes.oauth._oauth_token_repository import get_token

logger = logging.getLogger(__name__)

_GRAPH_VERSION = "v21.0"
_GRAPH_BASE = f"https://graph.facebook.com/{_GRAPH_VERSION}"
_HTTP_TIMEOUT = 12.0
# Métricas de página (lifetime/day) · best-effort: si Meta cambia nombres → empty honesto.
_PAGE_METRICS = "page_fans,page_impressions,page_post_engagements"
_METRIC_MAP = {
    "page_fans": "followers",
    "page_post_engagements": "engagement",
    "page_impressions": "reach",
}


def _extract_metrics(data: list[dict[str, object]]) -> dict[str, int]:
    """Mapea la respuesta de /insights (lista de series) a {followers, engagement, reach}."""
    out: dict[str, int] = {}
    for series in data:
        name = series.get("name")
        mapped = _METRIC_MAP.get(str(name))
        if not mapped:
            continue
        values = series.get("values")
        if isinstance(values, list) and values:
            last = values[-1]
            value = last.get("value") if isinstance(last, dict) else None
            if isinstance(value, (int, float)):
                out[mapped] = int(value)
    return out


async def fetch_meta_insights(client_id: str) -> dict[str, object]:
    """Token del cliente → Graph /{page_id}/insights → {followers, engagement, reach}. Honesto."""
    try:
        token = await get_token(client_id, "meta")
    except Exception as e:  # noqa: BLE001 · crypto/DB → honesto, no 500
        logger.info(f"meta chip token read failed · {e}")
        return {"state": "error", "metrics": None, "detail": "token_unavailable"}
    if not token:
        return {"state": "not_connected", "metrics": None, "detail": None}
    access_token = str(token.get("access_token") or "")
    _pid = token.get("external_account_id")
    page_id: Optional[str] = _pid if isinstance(_pid, str) else None
    if not access_token or not page_id:
        return {"state": "empty", "metrics": None, "detail": "no_page_linked"}
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as http:
            resp = await http.get(
                f"{_GRAPH_BASE}/{page_id}/insights",
                params={"metric": _PAGE_METRICS, "access_token": access_token},
            )
    except Exception as e:  # noqa: BLE001 · red/DNS/timeout → honesto
        logger.info(f"meta chip graph call failed · {e}")
        return {"state": "error", "metrics": None, "detail": "graph_unreachable"}
    if resp.status_code != 200:
        logger.info(f"meta chip graph {resp.status_code} · {resp.text[:160]}")
        return {"state": "error", "metrics": None, "detail": f"graph_{resp.status_code}"}
    data = resp.json().get("data")
    metrics = _extract_metrics(data if isinstance(data, list) else [])
    if not metrics:
        return {"state": "empty", "metrics": None, "detail": "no_metrics"}
    return {"state": "ok", "metrics": metrics, "detail": None}
