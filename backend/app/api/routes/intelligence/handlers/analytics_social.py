"""GET /intelligence/analytics · métricas sociales reales del negocio vía Zernio (DEBT-034 · live-read).

Per-negocio por **profileId** (la llave canónica · AISLADO · 403 si ajeno · MISMO patrón que chips.py). Honesto/
best-effort (regla GLOBAL cero-sintéticos): sin profileId → connected=False + message (empty honesto, NO ceros
que finjan datos) · Zernio falla → arrays vacíos + lo que sí llegó · NUNCA 500 · JAMÁS un número inventado.
followers/serie se resuelven por **profileId** (NO bound_ids · que son frágiles y vacíos en negocios sin
binding · ver DEBT-ANALYTICS-RESOLVER-PROFILEID). Cache mem TTL 15min (el dato es de ~24-48h · sin tabla/cron/
migración). NO toca el flujo de publicar (este adapter es solo-lectura).
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
from app.api.routes.intelligence import _analytics_metrics as met
from app.api.routes.intelligence import _analytics_repository as arepo
from app.api.routes.intelligence.models import (
    EngagementRow, EngagementSeriesPoint, GrowthPoint, HeatmapCell,
    PostsSeriesPoint, SocialAnalyticsResponse)
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


async def _cached(key: str, fn: Callable[..., Awaitable[Any]], *args: str) -> Any:
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
    if not profile_id:                                    # sin profile no hay nada que resolver (Milagrosa)
        return SocialAnalyticsResponse(connected=False, message=_NO_ACCOUNTS)

    accounts_api: List[Dict[str, Any]] = await _cached("accounts", za.list_accounts)
    daily = await _cached(f"daily:{profile_id}", za.daily_metrics, profile_id)
    best = await _cached(f"best:{profile_id}", za.best_time, profile_id)
    ig_ids = asm.ig_account_ids(accounts_api, profile_id)  # cuentas IG del profile (no bound_ids)
    ig_hist: List[Dict[str, Any]] = list(await asyncio.gather(
        *[_cached(f"fh:{aid}", za.follower_history, aid) for aid in ig_ids]))

    eng_rows = asm.engagement_by_network(daily)  # una vez · total_reach + ER derivan de aquí (consistencia)
    return SocialAnalyticsResponse(
        connected=True,
        growth=[GrowthPoint(**g) for g in asm.growth_series(ig_hist)],
        engagement=[EngagementRow(**e) for e in eng_rows],
        engagement_series=[EngagementSeriesPoint(**s) for s in met.engagement_series(daily)],
        posts_series=[PostsSeriesPoint(**p) for p in met.posts_series(daily)],
        heatmap=[HeatmapCell(**c) for c in asm.heatmap_cells(best)],
        total_followers=asm.followers_total(accounts_api, profile_id),
        total_reach=met.total_reach(eng_rows),
        profile_engagement=met.profile_engagement(eng_rows),
        best_hour=asm.best_hour(best),
        data_delay=_DELAY,
    )
