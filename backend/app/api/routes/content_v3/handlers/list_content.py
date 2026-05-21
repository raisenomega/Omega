"""GET /api/v1/content/ · lista content_lab_generated del usuario.

Query params: status=pending|saved|all · content_type · limit · offset.
DDD A1/A9: handler -> reader (NUNCA Supabase directo).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Query
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.api.routes.content_v3.models.content_models import ContentItem, ContentListResponse

router = APIRouter()

STATUS_TO_FLAG: dict[str, Optional[bool]] = {"pending": False, "saved": True, "all": None}


def _to_item(row: dict) -> ContentItem:
    sa = row.get("social_accounts")
    platform = sa.get("platform") if isinstance(sa, dict) else None
    return ContentItem(
        id=str(row["id"]),
        client_id=str(row["client_id"]),
        platform=platform,
        content_type=row.get("content_type") or "",
        content=row.get("content") or "",
        model=row.get("model"),
        is_saved=bool(row.get("is_saved")),
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
    if status not in STATUS_TO_FLAG:
        raise HTTPException(status_code=422, detail="invalid_status")
    is_saved = STATUS_TO_FLAG[status]
    client_ids = reader.get_accessible_client_ids(user["id"])
    rows = reader.list_content(client_ids, is_saved, content_type, limit, offset)
    total = reader.count_content(client_ids, is_saved, content_type)
    return ContentListResponse(items=[_to_item(r) for r in rows], total=total)
