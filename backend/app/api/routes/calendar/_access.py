"""Access helpers calendar legacy · DEBT-CL-013 + cierre agujero seguridad C.

Los 4 endpoints calendar (POST/GET/PATCH/DELETE) NO tenían auth ni RBAC.
Este helper centraliza el patrón: lookup recurso + ownership check vía
user_owns_client (cliente propio o reseller dueño).

cross-BC helper · candidato a app.shared.access_control en refactor futuro
(hoy: clients_v3._clients_reader + clients_v3._access_control son helpers
puros sin imports externos · pragmático importar desde aquí).
"""
from typing import Any
from fastapi import HTTPException

# cross-BC helper · candidato a app.shared.access_control
from app.api.routes.clients_v3 import _clients_reader as clients_reader
from app.api.routes.clients_v3._access_control import user_owns_client


def resolve_client_or_403(user_id: str, client_id: str) -> dict[str, Any]:
    """Lookup client + ownership check. Raise 404/403."""
    client = clients_reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user_id, client):
        raise HTTPException(status_code=403, detail="client_access_denied")
    return client


def resolve_account_or_403(supabase, account_id: str, user_id: str) -> dict[str, Any]:
    """Lookup social_account + cliente asociado + ownership check. Raise 404/403."""
    r = supabase.client.table("social_accounts").select(
        "*, clients!inner(*)"
    ).eq("id", account_id).execute()
    if not r.data:
        raise HTTPException(status_code=404, detail="account_not_found")
    account = r.data[0]
    client = account.get("clients") or {}
    if not user_owns_client(user_id, client):
        raise HTTPException(status_code=403, detail="account_access_denied")
    return account


def resolve_account_by_client_platform_or_404(
    supabase, client_id: str, platform: str
) -> dict[str, Any]:
    """Lookup primary account por (client_id, platform). Caller debe haber
    validado ownership del client_id previamente. Raise 404 si no hay cuenta."""
    r = supabase.client.table("social_accounts").select("*").eq(
        "client_id", client_id
    ).eq("platform", platform).order(
        "is_primary", desc=True
    ).limit(1).execute()
    if not r.data:
        raise HTTPException(
            status_code=404,
            detail=f"no_account_for_platform:{platform}",
        )
    return r.data[0]


def resolve_post_or_403(supabase, post_id: str, user_id: str) -> dict[str, Any]:
    """Lookup post + cliente asociado + ownership. Raise 404/403."""
    r = supabase.client.table("scheduled_posts").select("*").eq("id", post_id).execute()
    if not r.data:
        raise HTTPException(status_code=404, detail="post_not_found")
    post = r.data[0]
    client_id = str(post.get("client_id") or "")
    if not client_id:
        raise HTTPException(status_code=404, detail="post_not_found")  # no leak orphan
    resolve_client_or_403(user_id, client_id)  # raises 403 si no owner
    return post
