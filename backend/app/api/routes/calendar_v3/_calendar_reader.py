"""Repository reads · calendar_v3 · DDD A1/A9."""
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service


def _sb():
    return get_supabase_service().client


def get_accessible_client_ids(user_id: str) -> list[str]:
    """Client IDs visibles: cliente propio O reseller dueño."""
    sb = _sb()
    own = sb.table("clients").select("id").eq("user_id", user_id).execute()
    ids: set[str] = {str(c["id"]) for c in (own.data or [])}
    res = sb.table("resellers").select("id").eq("owner_user_id", user_id).execute()
    reseller_ids = [str(r["id"]) for r in (res.data or [])]
    if reseller_ids:
        managed = sb.table("clients").select("id").in_("reseller_id", reseller_ids).execute()
        ids.update(str(c["id"]) for c in (managed.data or []))
    return list(ids)


def month_to_range(month: str) -> tuple[str, str]:
    """YYYY-MM -> (start, end_exclusive) ISO date strings · maneja overflow Dec->Jan."""
    year, mo = int(month[:4]), int(month[5:7])
    start = f"{year:04d}-{mo:02d}-01"
    end = f"{year + 1:04d}-01-01" if mo == 12 else f"{year:04d}-{mo + 1:02d}-01"
    return (start, end)


def list_scheduled_posts(client_ids: list[str], month: Optional[str], status: Optional[str]) -> list[dict[str, Any]]:
    if not client_ids:
        return []
    q = _sb().table("scheduled_posts").select(
        "*, social_accounts(platform), content_lab_generated(content)"
    ).in_("client_id", client_ids)
    if month:
        start, end = month_to_range(month)
        q = q.gte("scheduled_for", start).lt("scheduled_for", end)
    if status:
        q = q.eq("status", status)
    r = q.order("scheduled_for", desc=False).execute()
    return r.data or []


def get_scheduled_post(post_id: str) -> Optional[dict[str, Any]]:
    r = _sb().table("scheduled_posts").select("*").eq("id", post_id).limit(1).execute()
    return r.data[0] if r.data else None
