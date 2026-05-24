"""Access helpers calendar_v3 · DEBT-CL-017 + path X.

Helpers independientes de calendar/_access.py legacy para preservar
ground truth V3 (si owner elimina legacy en refactor futuro, V3 sigue
funcionando intacto).

cross-BC helper · candidato a app.shared.access_control cuando crezca
el número de consumidores (>=3 BCs distintos).
"""
from typing import Any
from fastapi import HTTPException

# cross-BC helper · candidato a app.shared.access_control
from app.api.routes.clients_v3 import _clients_reader as clients_reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.infrastructure.supabase_service import get_supabase_service


def resolve_client_or_403(user_id: str, client_id: str) -> dict[str, Any]:
    """Lookup client + ownership check. Raise 404/403."""
    client = clients_reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user_id, client):
        raise HTTPException(status_code=403, detail="client_access_denied")
    return client


def resolve_account_by_client_platform_or_404(client_id: str, platform: str) -> dict[str, Any]:
    """Lookup primary social_account por (client_id, platform). Caller debe
    validar ownership del client_id previamente. Raise 404 si sin cuenta."""
    sb = get_supabase_service().client
    r = sb.table("social_accounts").select("id, platform").eq(
        "client_id", client_id,
    ).eq("platform", platform).order(
        "is_primary", desc=True,
    ).limit(1).execute()
    if not r.data:
        raise HTTPException(
            status_code=404,
            detail=f"no_account_for_platform:{platform}",
        )
    return r.data[0]
