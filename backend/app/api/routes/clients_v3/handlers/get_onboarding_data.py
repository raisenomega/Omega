"""GET /api/v1/clients/{client_id}/onboarding-data · datos completos para editar wizard.

DDD A1/A9: handler -> reader (NUNCA Supabase directo).
"""
from typing import Any, Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3._payload_transform import to_onboarding_payload

router = APIRouter()


@router.get("/{client_id}/onboarding-data")
async def get_onboarding_data(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> dict[str, Any]:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="access_denied")
    context = reader.get_client_context(client_id)
    accounts = reader.get_social_accounts(client_id)
    assets = reader.get_brand_assets(client_id)
    samples = reader.get_brand_voice_samples_manual(client_id)
    return to_onboarding_payload(client, context, accounts, assets, samples)
