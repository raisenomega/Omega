"""GET /intelligence/chips/meta · /intelligence/chips/google · Centro de Inteligencia Fase 2.

Auth: JWT → cliente propio del usuario (find_client_for_user · mismo patrón que los flujos
OAuth de RONDA D). Cada chip lee el token del cliente y consulta la API real del proveedor.

Honesto (regla cero-mocks · CI-R1):
  · sin token → connected=False + message "Conectá ..." (jamás un número inventado).
  · API falla/sin datos → connected refleja el token, metrics=None + message del porqué.
NUNCA 500: los helpers son best-effort y devuelven un estado tipado, nunca levantan.
"""
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.intelligence import _intelligence_repository as intel_repo
from app.api.routes.intelligence._google_insights import fetch_google_insights
from app.api.routes.intelligence._meta_insights import fetch_meta_insights
from app.api.routes.intelligence.models import ChipResponse

router = APIRouter()

_NOT_CONNECTED_META = "Conectá Meta para ver tus métricas reales (seguidores, engagement, alcance)."
_NOT_CONNECTED_GOOGLE = "Conectá Google para ver tus métricas reales (sesiones, clics, impresiones)."
_EMPTY = "Conectado, pero todavía no hay métricas disponibles para mostrar."
_ERROR = "No pudimos leer las métricas en este momento. Reintentá en unos minutos."


async def _resolve_client_id(authorization: Optional[str], client_id: Optional[str] = None) -> str:
    """Switcher V1: client_id presente → negocio activo validado (403 si ajeno). Ausente → legacy LIMIT 1."""
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id) if client_id else repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    return str(client["id"])


def _to_response(result: dict[str, object], not_connected_msg: str) -> ChipResponse:
    """Mapea el estado tipado del helper a ChipResponse honesto (sin fabricar datos)."""
    state = result.get("state")
    if state == "ok":
        metrics = result.get("metrics")
        return ChipResponse(connected=True, metrics=metrics if isinstance(metrics, dict) else None)
    if state == "not_connected":
        return ChipResponse(connected=False, metrics=None, message=not_connected_msg)
    if state == "empty":
        return ChipResponse(connected=True, metrics=None, message=_EMPTY)
    return ChipResponse(connected=True, metrics=None, message=_ERROR)


@router.get("/chips/meta", response_model=ChipResponse)
async def meta_chip(
    authorization: Optional[str] = Header(None),
    client_id: Optional[str] = Query(None),  # Switcher V1: negocio activo · ausente → legacy
) -> ChipResponse:
    """Métricas reales de Meta del cliente · honesto si no está conectado."""
    resolved = await _resolve_client_id(authorization, client_id)
    result = await fetch_meta_insights(resolved)
    return _to_response(result, _NOT_CONNECTED_META)


@router.get("/chips/google", response_model=ChipResponse)
async def google_chip(
    authorization: Optional[str] = Header(None),
    client_id: Optional[str] = Query(None),  # Switcher V1: negocio activo · ausente → legacy
) -> ChipResponse:
    """Métricas reales de Google (GA4 + Search Console) del cliente · honesto si no conectado."""
    resolved = await _resolve_client_id(authorization, client_id)
    site = intel_repo.get_client_site(resolved)
    site_url = site.get("website") if isinstance(site, dict) else None
    result = await fetch_google_insights(resolved, site_url if isinstance(site_url, str) else None)
    return _to_response(result, _NOT_CONNECTED_GOOGLE)
