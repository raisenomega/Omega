"""GA4 property picker (Vía A) · lista las propiedades GA4 del cliente conectado y persiste la
elegida en oauth_tokens.external_account_id (el property_id que _google_insights usa para GA4).
Ownership vía resolve_client_or_403 (mismo patrón que el resto). NO escribe token · sin scope nuevo."""
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.oauth._ga4_admin import list_ga4_properties
from app.api.routes.oauth._oauth_token_repository import set_external_account_id

router = APIRouter()


async def _owned_client_id(client_id: str, authorization: Optional[str]) -> str:
    """client_id del Switcher + ownership verbatim (resolve_client_or_403). 404 si no existe · 403 si ajeno."""
    user = await get_current_user(authorization)
    return str(resolve_client_or_403(user["id"], client_id)["id"])


class PropertyBody(BaseModel):
    property_id: str


@router.get("/google/properties")
async def google_properties(client_id: str = Query(...),
                            authorization: Optional[str] = Header(None)) -> dict[str, object]:
    """Lista [{property_id, display_name}] de las propiedades GA4 del cliente (honesto · [] si no hay)."""
    actor_client_id = await _owned_client_id(client_id, authorization)
    return {"properties": await list_ga4_properties(actor_client_id)}


@router.post("/google/property")
async def set_google_property(body: PropertyBody, client_id: str = Query(...),
                              authorization: Optional[str] = Header(None)) -> dict[str, object]:
    """Persiste el property_id elegido en external_account_id de la fila google del cliente.
    property_id vacío → 400 · sin fila (no conectado) → 404."""
    pid = body.property_id.strip()
    if not pid:
        raise HTTPException(status_code=400, detail="property_id_required")
    actor_client_id = await _owned_client_id(client_id, authorization)
    updated = await set_external_account_id(actor_client_id, "google", pid)
    if not updated:
        raise HTTPException(status_code=404, detail="google_not_connected")
    return {"ok": True, "property_id": pid}
