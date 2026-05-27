"""PATCH /api/v1/content/{id}/save · is_saved bool API <-> status DB (draft/approved).

Transición draft->approved dispara aprendizaje ARIA:
  · safe_insert agent_memory (brand_voice · approved_by_client · conf=10)
  · safe_insert brand_voice_corpus (source=approved_draft)
approved->draft: solo cambio de status (preserva señal histórica).
DDD A1/A9: handler -> repo + reader.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader, _content_repository as repo
from app.api.routes.content_v3.models.content_models import SaveContentRequest

router = APIRouter()


@router.patch("/{content_id}/save")
async def save_content(
    content_id: str,
    request: SaveContentRequest,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    item = reader.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="content_not_found")
    accessible = reader.get_accessible_client_ids(user["id"])
    if str(item.get("client_id")) not in accessible:
        raise HTTPException(status_code=403, detail="access_denied")

    was_approved = item.get("status") == "approved"
    new_status = "approved" if request.is_saved else "draft"
    await repo.safe_insert("update_status", repo.update_status, content_id, new_status)

    if request.is_saved and not was_approved:
        text = item.get("generated_text") or ""  # col real
        client_id = str(item["client_id"])
        await repo.safe_insert("corpus", repo.insert_brand_voice_corpus_approved, client_id, text, None)
        await repo.safe_insert("memory", repo.insert_agent_memory_approved, user["id"], client_id, text)

    return {"id": content_id, "is_saved": request.is_saved}
