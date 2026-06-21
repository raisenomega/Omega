"""Adapter Zernio Analytics · lectura best-effort de métricas (DEBT-034 · live-read · 21 jun).

Misma key/base que zernio_adapter (publish) · SOLO GET de analytics · NO toca el flujo de publicar.
Fail-safe honesto (regla cero-mocks · igual que publish/HERMES): error/timeout/non-2xx → {} · el caller
arma el empty honesto · JAMÁS inventa un número. Contrato verificado EN VIVO (21 jun): daily-metrics y
best-time por profileId (negocio agregado) · follower-history (serie) solo Instagram · insights por cuenta
con path por plataforma (FB=page-insights/page_follows · TikTok=account-insights/follower_count).
"""
import logging
from typing import Any, Dict

import httpx

from app.bc_cognition.infrastructure.zernio_config import get_zernio_settings

logger = logging.getLogger(__name__)
_HTTP_TIMEOUT = 30.0

# Path de insights por plataforma (nombres distintos · verificado en vivo).
INSIGHTS_PATH: Dict[str, str] = {
    "instagram": "instagram/account-insights", "facebook": "facebook/page-insights",
    "tiktok": "tiktok/account-insights", "youtube": "youtube/channel-insights",
    "linkedin": "linkedin/aggregate",
}
# Campo de seguidores por plataforma (IG/TikTok = follower_count · FB = page_follows).
FOLLOWER_FIELD: Dict[str, str] = {
    "instagram": "follower_count", "facebook": "page_follows", "tiktok": "follower_count",
    "youtube": "follower_count", "linkedin": "follower_count",
}


def _conf() -> "tuple[Dict[str, str], str]":
    s = get_zernio_settings()
    if not s.zernio_api_key.strip():
        return {}, ""
    return {"Authorization": f"Bearer {s.zernio_api_key}"}, s.zernio_api_base


async def _get(path: str, params: Dict[str, str]) -> Dict[str, Any]:
    """GET best-effort · {} ante cualquier fallo (sin key · transporte · non-2xx). Nunca levanta."""
    headers, base = _conf()
    if not base:
        return {}
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as c:
            r = await c.get(f"{base}{path}", params=params)
        if r.status_code != 200:
            logger.warning(f"zernio analytics {path} -> {r.status_code}")
            return {}
        d = r.json()
        return d if isinstance(d, dict) else {"items": d}
    except Exception as e:  # noqa: BLE001 · observabilidad · best-effort honesto
        logger.warning(f"zernio analytics {path} fallo (best-effort): {e}")
        return {}


async def daily_metrics(profile_id: str) -> Dict[str, Any]:
    return await _get("/analytics/daily-metrics", {"profileId": profile_id})


async def best_time(profile_id: str) -> Dict[str, Any]:
    return await _get("/analytics/best-time", {"profileId": profile_id})


async def follower_history(account_id: str) -> Dict[str, Any]:
    """Serie diaria de seguidores · SOLO Instagram (path confirmado · FB/TikTok via insights)."""
    return await _get("/analytics/instagram/follower-history",
                      {"accountId": account_id, "metricType": "time_series"})


async def insights(account_id: str, platform: str) -> Dict[str, Any]:
    """Insights por cuenta (incluye seguidores actuales · campo por plataforma · FOLLOWER_FIELD)."""
    path = INSIGHTS_PATH.get(platform)
    return await _get(f"/analytics/{path}", {"accountId": account_id}) if path else {}
