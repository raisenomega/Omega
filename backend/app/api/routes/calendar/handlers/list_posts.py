"""Handler: List Posts · auth + RBAC obligatorios (G-capas).

Cierra agujero seguridad: ahora get_current_user + ownership check antes de
exponer cualquier scheduled_post. Si user_id query param presente, DEBE ser
igual al user del JWT (cero leak cross-user). Si ninguno presente, default
al user del JWT (sane default).
"""
import logging
from typing import Optional
from fastapi import HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar.models import ScheduledPostListResponse, ScheduledPostResponse
from app.api.routes.calendar._access import resolve_account_or_403, resolve_client_or_403
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_list_posts(
    authorization: Optional[str],
    account_id: Optional[str] = None,
    client_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
) -> ScheduledPostListResponse:
    user = await get_current_user(authorization)
    auth_user_id = user["id"]
    supabase = get_supabase_service()
    repo = ScheduledPostRepository(supabase)

    # Ownership check según path · cualquier leak cross-user es 403
    if user_id and user_id != auth_user_id:
        raise HTTPException(403, "user_id_mismatch")
    if account_id:
        resolve_account_or_403(supabase, account_id, auth_user_id)
    elif client_id:
        resolve_client_or_403(auth_user_id, client_id)
    # else: default a auth_user_id (sane default)

    # Resolver client_ids efectivos para filter (puede ser N clientes del user)
    effective_user_id = user_id or (None if account_id or client_id else auth_user_id)
    client_ids: list[str] = []
    if effective_user_id:
        r = supabase.client.table("clients").select("id").eq("user_id", effective_user_id).execute()
        client_ids = [c["id"] for c in (r.data or [])]
        if not client_ids:
            return ScheduledPostListResponse(items=[], total=0, limit=limit, offset=offset)

    query = supabase.client.table("scheduled_posts").select("*")
    if account_id:
        query = query.eq("account_id", account_id)
    elif client_id:
        query = query.eq("client_id", client_id)
    elif client_ids:
        query = query.in_("client_id", client_ids)
    if status:
        query = query.eq("status", status)
    query = query.order("scheduled_date", desc=False).order("scheduled_time", desc=False).range(offset, offset + limit - 1)

    response = query.execute()
    posts = [repo._map_to_entity(row) for row in (response.data or [])]
    items = [
        ScheduledPostResponse(
            id=p.id, client_id=p.client_id, account_id=p.account_id,
            content_lab_id=p.content_lab_id, content_type=p.content_type,
            text_content=p.text_content, image_url=p.image_url,
            hashtags=p.hashtags, scheduled_date=p.scheduled_date,
            scheduled_time=p.scheduled_time, timezone=p.timezone,
            status=p.status, agent_assigned=p.agent_assigned, is_active=p.is_active,
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else "",
        ) for p in posts
    ]
    logger.info(f"list_posts · user={auth_user_id} · returned {len(items)}")
    return ScheduledPostListResponse(items=items, total=len(items), limit=limit, offset=offset)
