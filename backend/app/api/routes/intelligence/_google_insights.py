"""Google insights helper · Centro de Inteligencia Fase 2 (chip Google).

Lee el token OAuth del cliente (get_token · RONDA D, read-only) y consulta dos APIs con
ese token: GA4 Data API (runReport · sessions) y Search Console (searchanalytics · clicks +
impressions). Best-effort + honesto (regla cero-mocks · CI-R1/CI-R7):
  · sin token             → {"state": "not_connected"}
  · APIs fallan/sin datos → {"state": "error"/"empty"} (nunca levanta · nunca 500)
  · ok (≥1 métrica real)  → {"state": "ok", "metrics": {sessions, clicks, impressions}}

external_account_id se interpreta como GA4 property id (numérico) si está presente. La URL del
sitio para Search Console viene de la tabla clients (site_url param). NO escribe · NO toca oauth/.
"""
import logging
from typing import Optional
from urllib.parse import quote

import httpx

from app.api.routes.oauth._oauth_token_repository import get_token

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 12.0
_GA4_BASE = "https://analyticsdata.googleapis.com/v1beta"
_GSC_BASE = "https://searchconsole.googleapis.com/webmasters/v3"


async def _ga4_sessions(http: httpx.AsyncClient, token: str, property_id: str) -> Optional[int]:
    """runReport last 7d → suma de sessions. None si falla/sin datos (best-effort)."""
    try:
        resp = await http.post(
            f"{_GA4_BASE}/properties/{property_id}:runReport",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
                "metrics": [{"name": "sessions"}],
            },
        )
    except Exception as e:  # noqa: BLE001 · honesto
        logger.info(f"google chip ga4 call failed · {e}")
        return None
    if resp.status_code != 200:
        logger.info(f"google chip ga4 {resp.status_code} · {resp.text[:160]}")
        return None
    rows = resp.json().get("rows")
    if not isinstance(rows, list) or not rows:
        return None
    total = 0
    for row in rows:
        vals = row.get("metricValues") if isinstance(row, dict) else None
        if isinstance(vals, list) and vals and isinstance(vals[0], dict):
            try:
                total += int(float(vals[0].get("value", 0)))
            except (TypeError, ValueError):
                continue
    return total


async def _gsc_search(http: httpx.AsyncClient, token: str, site_url: str) -> dict[str, int]:
    """searchanalytics.query last 7d → {clicks, impressions} agregados. {} si falla/sin datos."""
    try:
        resp = await http.post(
            f"{_GSC_BASE}/sites/{quote(site_url, safe='')}/searchAnalytics/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"startDate": "2024-01-01", "endDate": "2030-01-01", "rowLimit": 1},
        )
    except Exception as e:  # noqa: BLE001 · honesto
        logger.info(f"google chip gsc call failed · {e}")
        return {}
    if resp.status_code != 200:
        logger.info(f"google chip gsc {resp.status_code} · {resp.text[:160]}")
        return {}
    rows = resp.json().get("rows")
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        return {}
    row = rows[0]
    out: dict[str, int] = {}
    if isinstance(row.get("clicks"), (int, float)):
        out["clicks"] = int(row["clicks"])
    if isinstance(row.get("impressions"), (int, float)):
        out["impressions"] = int(row["impressions"])
    return out


async def fetch_google_insights(client_id: str, site_url: Optional[str]) -> dict[str, object]:
    """Token del cliente → GA4 + Search Console → {sessions, clicks, impressions}. Honesto."""
    try:
        token = await get_token(client_id, "google")
    except Exception as e:  # noqa: BLE001 · crypto/DB → honesto, no 500
        logger.info(f"google chip token read failed · {e}")
        return {"state": "error", "metrics": None, "detail": "token_unavailable"}
    if not token:
        return {"state": "not_connected", "metrics": None, "detail": None}
    access_token = str(token.get("access_token") or "")
    if not access_token:
        return {"state": "empty", "metrics": None, "detail": "no_access_token"}
    _pid = token.get("external_account_id")
    property_id: Optional[str] = _pid if isinstance(_pid, str) else None
    metrics: dict[str, int] = {}
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as http:
        if property_id:
            sessions = await _ga4_sessions(http, access_token, str(property_id))
            if sessions is not None:
                metrics["sessions"] = sessions
        if site_url:
            metrics.update(await _gsc_search(http, access_token, site_url))
    if not metrics:
        return {"state": "empty", "metrics": None, "detail": "no_metrics"}
    return {"state": "ok", "metrics": metrics, "detail": None}
