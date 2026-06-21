"""Adapter Zernio Analytics · lectura best-effort (DEBT-034 · live-read · "paridad de verdad" 21 jun).

Misma key/base que zernio_adapter (publish) · SOLO GET de analytics · NO toca el flujo de publicar.
Fail-safe honesto (regla GLOBAL cero-sintéticos): error/timeout/non-2xx → {} (o [] en listas) · el caller
arma el empty honesto · JAMÁS inventa un número. Contrato verificado EN VIVO (21 jun):
  · /accounts → cada cuenta trae followersCount (snapshot actual) + externalPostCount (posts reales).
  · daily-metrics / best-time por profileId (negocio agregado).
  · follower-history (serie diaria) SOLO Instagram (FB/TikTok → 404).
NO se lee page_follows (era suma de ventana · raíz del bug "28 seguidores").
"""
import logging
from typing import Any, Dict, List

import httpx

from app.bc_cognition.infrastructure.zernio_config import get_zernio_settings

logger = logging.getLogger(__name__)
_HTTP_TIMEOUT = 30.0


def _conf() -> "tuple[Dict[str, str], str]":
    s = get_zernio_settings()
    if not s.zernio_api_key.strip():
        return {}, ""
    return {"Authorization": f"Bearer {s.zernio_api_key}"}, s.zernio_api_base


async def _get(path: str, params: Dict[str, str]) -> Any:
    """GET best-effort · None ante cualquier fallo (sin key · transporte · non-2xx). Nunca levanta."""
    headers, base = _conf()
    if not base:
        return None
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as c:
            r = await c.get(f"{base}{path}", params=params)
        if r.status_code != 200:
            logger.warning(f"zernio analytics {path} -> {r.status_code}")
            return None
        return r.json()
    except Exception as e:  # noqa: BLE001 · observabilidad · best-effort honesto
        logger.warning(f"zernio analytics {path} fallo (best-effort): {e}")
        return None


async def list_accounts() -> List[Dict[str, Any]]:
    """Todas las cuentas del workspace (followersCount + externalPostCount) · [] si falla."""
    d = await _get("/accounts", {})
    if isinstance(d, dict):
        accs = d.get("accounts")
        return accs if isinstance(accs, list) else []
    return d if isinstance(d, list) else []


async def daily_metrics(profile_id: str) -> Dict[str, Any]:
    d = await _get("/analytics/daily-metrics", {"profileId": profile_id})
    return d if isinstance(d, dict) else {}


async def best_time(profile_id: str) -> Dict[str, Any]:
    d = await _get("/analytics/best-time", {"profileId": profile_id})
    return d if isinstance(d, dict) else {}


async def follower_history(account_id: str) -> Dict[str, Any]:
    """Serie diaria de seguidores · SOLO Instagram (path confirmado · para el GrowthChart)."""
    d = await _get("/analytics/instagram/follower-history",
                   {"accountId": account_id, "metricType": "time_series"})
    return d if isinstance(d, dict) else {}
