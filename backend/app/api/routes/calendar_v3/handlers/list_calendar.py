"""GET /api/v1/calendar/ · scheduled_posts del mes con JOIN platform+content.

Mapeo UI->DB: status='scheduled' (UI) -> 'pending' (DB).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Query
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar_v3 import _calendar_reader as reader
from app.api.routes.calendar_v3.models.calendar_models import CalendarPost, CalendarListResponse

router = APIRouter()

UI_TO_DB_STATUS = {
    "scheduled": "pending",
    "published": "published",
    "failed": "failed",
    "cancelled": "cancelled",
    "publishing": "publishing",
    "all": None,
}


def _to_item(row: dict) -> CalendarPost:
    sa = row.get("social_accounts")
    platform = sa.get("platform") if isinstance(sa, dict) else None
    cl = row.get("content_lab_generated")
    preview = (cl.get("generated_text") or "") if isinstance(cl, dict) else ""
    return CalendarPost(
        id=str(row["id"]),
        client_id=str(row["client_id"]),
        platform=platform,
        content_preview=preview[:200],
        scheduled_for=str(row.get("scheduled_for") or ""),
        status=str(row.get("status") or ""),
        platform_post_id=row.get("platform_post_id"),
        error_message=row.get("error_message"),
    )


@router.get("/", response_model=CalendarListResponse)
async def list_calendar(
    month: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$"),
    status: str = Query("all"),
    authorization: Optional[str] = Header(None),
) -> CalendarListResponse:
    user = await get_current_user(authorization)
    if status not in UI_TO_DB_STATUS:
        raise HTTPException(status_code=422, detail="invalid_status")
    db_status = UI_TO_DB_STATUS[status]
    client_ids = reader.get_accessible_client_ids(user["id"])
    rows = reader.list_scheduled_posts(client_ids, month, db_status)
    return CalendarListResponse(items=[_to_item(r) for r in rows], total=len(rows))
