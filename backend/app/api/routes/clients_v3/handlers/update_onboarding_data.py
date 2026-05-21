"""PATCH /api/v1/clients/{client_id}/onboarding-data · UPDATE wizard completo.

DDD A1/A9: handler -> repo + reader (NUNCA Supabase directo).
Replace strategy social_accounts: DELETE all + INSERT new (DEBT-040 caveat ·
sin OAuth tokens hoy = seguro · Fase 2 cambiar a UPSERT por (client_id, platform, username)).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_repository as repo, _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3._onboarding_helpers import calc_completion_percent, validate_payload
from app.api.routes.clients_v3.handlers.create_client_onboarding import _build_context
from app.api.routes.clients_v3.models.onboarding import OnboardingPayload, OnboardingResponse

router = APIRouter()


@router.patch("/{client_id}/onboarding-data", response_model=OnboardingResponse)
async def update_onboarding_data(
    client_id: str,
    payload: OnboardingPayload,
    authorization: Optional[str] = Header(None),
) -> OnboardingResponse:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="access_denied")
    ok, err = validate_payload(payload)
    if not ok:
        raise HTTPException(status_code=422, detail=err)

    identity_dict = payload.identity.model_dump()
    regions = identity_dict.pop("regions")
    identity_dict["region"] = ",".join(regions)
    repo.safe_insert("update_client", repo.update_client_by_id, client_id, identity_dict)

    completion = calc_completion_percent(payload)
    repo.safe_insert("update_context", repo.upsert_client_context, client_id, _build_context(payload, completion))
    repo.safe_insert("delete_accounts", repo.delete_social_accounts, client_id)
    repo.safe_insert("insert_accounts", repo.bulk_insert_social_accounts, client_id, [a.model_dump() for a in payload.social_accounts])
    if payload.brand_assets is not None:
        repo.safe_insert("brand_assets", repo.upsert_brand_assets, client_id, payload.brand_assets.model_dump())
    repo.safe_insert("memory", repo.insert_agent_memory, user["id"], client_id,
                     f"Cliente {client.get('name')} actualizó su perfil",
                     "Datos del cliente actualizados · context disponible para todos los agentes", 10)
    return OnboardingResponse(client_id=client_id, completion_percent=completion, onboarding_complete=completion >= 80)
