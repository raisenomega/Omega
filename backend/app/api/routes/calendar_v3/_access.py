"""Access helpers calendar_v3 · DEBT-CL-017 + path X.

Helpers independientes de calendar/_access.py legacy para preservar
ground truth V3 (si owner elimina legacy en refactor futuro, V3 sigue
funcionando intacto).

cross-BC helper · candidato a app.shared.access_control cuando crezca
el número de consumidores (>=3 BCs distintos).
"""
from typing import Any, Optional
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


def first_active_account_id_or_none(client_id: str, platform: str) -> Optional[str]:
    """E (fan-out multi-red) · gemelo NO-LANZANTE de resolve_account_by_client_platform_or_404.
    Misma query que _supervised_approve._first_active_account_id (probada en prod): primera cuenta
    status='active' de la plataforma. None si no hay -> la red marcada se OMITE del fan-out (jamas
    se inventa cuenta · invariante social_account_id NUNCA NULL). Vive aca (no en content_v3) para
    no acoplar bounded contexts."""
    if not platform:
        return None
    sb = get_supabase_service().client
    r = sb.table("social_accounts").select("id").eq("client_id", client_id).eq(
        "platform", platform).eq("status", "active").order("created_at").limit(1).execute()
    return str(r.data[0]["id"]) if r.data else None


def resolve_account_by_client_platform_or_404(client_id: str, platform: str) -> dict[str, Any]:
    """Lookup primera cuenta activa por (client_id, platform). Fallback cuando
    user no eligió cuenta específica (DEBT-CL-015 · ver resolve_account_by_id_or_403).

    Fix latente DEBT-CL-015 (23 may 2026): ordenaba por 'is_primary' col que
    NO existe en schema V3 · ahora filtra status='active' + ORDER BY
    created_at ASC (deterministic · primera creada)."""
    sb = get_supabase_service().client
    r = sb.table("social_accounts").select("id, platform").eq(
        "client_id", client_id,
    ).eq("platform", platform).eq(
        "status", "active",
    ).order("created_at").limit(1).execute()
    if not r.data:
        raise HTTPException(
            status_code=404,
            detail=f"no_account_for_platform:{platform}",
        )
    return r.data[0]


def resolve_account_by_id_or_403(client_id: str, account_id: str) -> dict[str, Any]:
    """Lookup explícito de cuenta + valida pertenencia al client · status active.
    DEBT-CL-015: cuando user eligió cuenta específica del dropdown picker.
    Caller debe haber validado ownership del client_id previamente.
    Raise 404 si no existe · 403 si no pertenece · 400 si no active."""
    sb = get_supabase_service().client
    r = sb.table("social_accounts").select(
        "id, platform, client_id, status",
    ).eq("id", account_id).limit(1).execute()
    if not r.data:
        raise HTTPException(status_code=404, detail="account_not_found")
    account = r.data[0]
    if str(account.get("client_id") or "") != client_id:
        raise HTTPException(status_code=403, detail="account_access_denied")
    if account.get("status") != "active":
        raise HTTPException(status_code=400, detail=f"account_status:{account.get('status')}")
    return account
