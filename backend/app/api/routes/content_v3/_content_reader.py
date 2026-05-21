"""Repository reads · content_v3 · DDD A1/A9 read-only."""
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service


def _sb():
    return get_supabase_service().client


def get_accessible_client_ids(user_id: str) -> list[str]:
    """Client IDs visibles: cliente propio O cliente del reseller dueño."""
    sb = _sb()
    own = sb.table("clients").select("id").eq("user_id", user_id).execute()
    ids: set[str] = {str(c["id"]) for c in (own.data or [])}
    res = sb.table("resellers").select("id").eq("owner_user_id", user_id).execute()
    reseller_ids = [str(r["id"]) for r in (res.data or [])]
    if reseller_ids:
        managed = sb.table("clients").select("id").in_("reseller_id", reseller_ids).execute()
        ids.update(str(c["id"]) for c in (managed.data or []))
    return list(ids)


def list_content(client_ids: list[str], is_saved: Optional[bool], content_type: Optional[str], limit: int, offset: int) -> list[dict[str, Any]]:
    """Fetch content + merge platform en Python (evita FK ambiguity PostgREST embed)."""
    if not client_ids:
        return []
    sb = _sb()
    q = sb.table("content_lab_generated").select("*").in_("client_id", client_ids)
    if is_saved is not None:
        q = q.eq("is_saved", is_saved)
    if content_type:
        q = q.eq("content_type", content_type)
    items = q.order("created_at", desc=True).range(offset, offset + limit - 1).execute().data or []
    if not items:
        return []
    sa_ids = list({i["social_account_id"] for i in items if i.get("social_account_id")})
    sa_map: dict[str, dict] = {}
    if sa_ids:
        ar = sb.table("social_accounts").select("id, platform").in_("id", sa_ids).execute()
        sa_map = {str(a["id"]): a for a in (ar.data or [])}
    for i in items:
        sa_id = i.get("social_account_id")
        i["social_accounts"] = sa_map.get(str(sa_id)) if sa_id else None
    return items


def count_content(client_ids: list[str], is_saved: Optional[bool], content_type: Optional[str]) -> int:
    if not client_ids:
        return 0
    q = _sb().table("content_lab_generated").select("id", count="exact").in_("client_id", client_ids)
    if is_saved is not None:
        q = q.eq("is_saved", is_saved)
    if content_type:
        q = q.eq("content_type", content_type)
    r = q.execute()
    return r.count or 0


def get_content_item(content_id: str) -> Optional[dict[str, Any]]:
    r = _sb().table("content_lab_generated").select("*").eq("id", content_id).limit(1).execute()
    return r.data[0] if r.data else None
