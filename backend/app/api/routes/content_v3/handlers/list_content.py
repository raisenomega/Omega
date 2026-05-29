"""GET /api/v1/content/ · lista content_lab_generated del usuario.

Query params: status=pending|saved|all · content_type · limit · offset.
Mapeo UI->DB (schema real 00001:199): pending->draft · saved->approved.
DDD A1/A9: handler -> reader (NUNCA Supabase directo).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Query
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.api.routes.content_v3.models.content_models import ContentItem, ContentListResponse

router = APIRouter()

UI_TO_DB_STATUS: dict[str, Optional[str]] = {
    "pending": "draft", "saved": "approved", "all": None, "rejected": "rejected",  # rejected = tab Papelera
}


def _to_item(row: dict) -> ContentItem:
    return ContentItem(
        id=str(row["id"]),
        client_id=str(row["client_id"]),
        platform=None,  # schema real no tiene social_account_id en content_lab_generated
        content_type=row.get("content_type") or "",
        content=row.get("generated_text") or "",  # col real es generated_text
        model=row.get("agent_code"),  # proxy: agent_code (real col) en lugar de "model"
        is_saved=(row.get("status") == "approved"),  # derived from status
        created_at=str(row.get("created_at") or ""),
    )


@router.get("/", response_model=ContentListResponse)
async def list_content(
    status: str = Query("all"),
    content_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    authorization: Optional[str] = Header(None),
) -> ContentListResponse:
    user = await get_current_user(authorization)
    if status not in UI_TO_DB_STATUS:
        raise HTTPException(status_code=422, detail="invalid_status")
    db_status = UI_TO_DB_STATUS[status]
    client_ids = reader.get_accessible_client_ids(user["id"])
    rows = reader.list_content(client_ids, db_status, content_type, limit, offset)
    total = reader.count_content(client_ids, db_status, content_type)
    return ContentListResponse(items=[_to_item(r) for r in rows], total=total)
