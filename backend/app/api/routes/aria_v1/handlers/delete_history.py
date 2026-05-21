"""DELETE /api/v1/aria/history · borra conversaciones ARIA del user.

DDD A1/A9: handler -> aria_repository. Best-effort behavioral_event
(behavioral_events.chk_owner_present requiere client_id OR reseller_id).
"""
from typing import Optional
from fastapi import APIRouter, Header
from app.api.routes.auth.auth_utils import get_current_user
from app.bc_cognition.infrastructure import aria_repository as repo
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


@router.delete("/history")
async def delete_aria_history(
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    sb = get_supabase_service()
    repo.safe_insert("delete_history", repo.delete_aria_history, sb, user["id"])

    client = repo.safe_insert("find_client", repo.find_client_by_user, sb, user["id"])
    reseller = repo.safe_insert("find_reseller", repo.find_reseller_by_owner, sb, user["id"])
    client_id = client.get("id") if isinstance(client, dict) else None
    reseller_id = reseller.get("id") if isinstance(reseller, dict) else None
    if client_id or reseller_id:
        repo.safe_insert("behavioral", repo.insert_behavioral_event,
                         sb, user["id"], client_id, reseller_id,
                         "aria_history_cleared", {})
    return {"deleted": True}
