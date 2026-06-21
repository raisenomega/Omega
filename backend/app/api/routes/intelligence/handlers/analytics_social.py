"""GET /intelligence/analytics · métricas sociales reales del negocio vía Zernio (DEBT-034 · live-read).

Per-negocio por profileId (AISLADO · 403 si el client_id es ajeno · MISMO patrón que chips.py). Honesto/
best-effort (regla cero-mocks): sin profile/cuentas → connected=False + message (empty honesto, no ceros que
finjan datos) · Zernio falla → arrays vacíos + el dato que sí llegó · NUNCA 500 · JAMÁS inventa un número.
Cache en memoria TTL 15min (el dato es de ~24-48h · colapsa recargas · sin tabla/cron/migración).
NO toca el flujo de publicar (zernio_adapter.create_post intacto · este adapter es solo-lectura).
"""
import asyncio
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from fastapi import APIRouter, Header, HTTPException, Query

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.intelligence import _analytics_assembler as asm
from app.api.routes.intelligence import _analytics_repository as arepo
from app.api.routes.intelligence.models import (
    EngagementRow, GrowthPoint, HeatmapCell, SocialAnalyticsResponse)
from app.bc_cognition.infrastructure import zernio_analytics_adapter as za

router = APIRouter()
logger = logging.getLogger(__name__)

_DELAY = "Datos de Zernio · pueden tener hasta ~24-48h de retraso."
_NO_ACCOUNTS = "Conectá tus redes en Cuentas Sociales para ver tus métricas reales."

_TTL = 900.0  # 15 min · el dato de Zernio es de 24-48h, recargas más seguidas no aportan
_cache: Dict[str, Tuple[float, Any]] = {}


async def _resolve_client_id(authorization: Optional[str], client_id: Optional[str]) -> str:
    """Switcher V1: client_id presente → negocio activo validado (403 si ajeno). Ausente → legacy LIMIT 1."""
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id) if client_id else repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    return str(client["id"])


async def _cached(key: str, fn: Callable[..., Awaitable[Dict[str, Any]]], *args: str) -> Dict[str, Any]:
    """Memoiza la respuesta de Zernio por (endpoint, id) durante _TTL · best-effort (nunca levanta)."""
    now = time.monotonic()
    hit = _cache.get(key)
    if hit and now - hit[0] < _TTL:
        return hit[1]
    val = await fn(*args)
    _cache[key] = (now, val)
    return val


@router.get("/analytics", response_model=SocialAnalyticsResponse)
async def social_analytics(
    authorization: Optional[str] = Header(None),
    client_id: Optional[str] = Query(None),  # Switcher V1: negocio activo · ausente → legacy
) -> SocialAnalyticsResponse:
    """Analytics sociales reales del negocio · honesto si no hay profile/cuentas · nunca 500."""
    cid = await _resolve_client_id(authorization, client_id)
    profile_id = arepo.get_zernio_profile_id(cid)
    accounts = arepo.get_zernio_accounts(cid)
    if not profile_id and not accounts:
        return SocialAnalyticsResponse(connected=False, message=_NO_ACCOUNTS)

    daily = await _cached(f"daily:{profile_id}", za.daily_metrics, profile_id) if profile_id else {}
    best = await _cached(f"best:{profile_id}", za.best_time, profile_id) if profile_id else {}

    ig = [a for a in accounts if a["platform"] == "instagram"]
    other = [a for a in accounts if a["platform"] != "instagram"]
    ig_hist: List[Dict[str, Any]] = list(await asyncio.gather(
        *[_cached(f"fh:{a['account_id']}", za.follower_history, a["account_id"]) for a in ig]))
    other_ins: List[Dict[str, Any]] = list(await asyncio.gather(
        *[_cached(f"ins:{a['account_id']}", za.insights, a["account_id"], a["platform"]) for a in other]))
    per_account: List[Tuple[str, Dict[str, Any]]] = (
        [("instagram", h) for h in ig_hist] + list(zip([a["platform"] for a in other], other_ins)))

    return SocialAnalyticsResponse(
        connected=True,
        growth=[GrowthPoint(**g) for g in asm.growth_series(ig_hist)],
        engagement=[EngagementRow(**e) for e in asm.engagement_rows(daily)],
        heatmap=[HeatmapCell(**c) for c in asm.heatmap_cells(best)],
        total_followers=asm.followers_total(per_account),
        avg_engagement=asm.avg_engagement(daily),
        posts=asm.posts_count(daily),
        data_delay=_DELAY,
    )
