"""Modo Supervisado · adjuntar foto de la Biblioteca a un draft (content_lab_generated.media_urls).
P1: NO toca generated_text (caption+hashtags se preservan) · la foto va a media_urls. Ownership vía
accessible_client_ids. La foto fluye al publisher al aprobar (_supervised_approve → scheduled_posts.media_url)."""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader, _content_repository as repo

router = APIRouter()


class SetMediaRequest(BaseModel):
    media_urls: list[str]


@router.patch("/{content_id}/media")
async def set_media(content_id: str, request: SetMediaRequest, authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    item = reader.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="content_not_found")
    if str(item.get("client_id")) not in reader.get_accessible_client_ids(user["id"]):
        raise HTTPException(status_code=403, detail="access_denied")
    await repo.safe_insert("set_media", repo.update_media_urls, content_id, request.media_urls)
    return {"id": content_id, "media_urls": request.media_urls}
