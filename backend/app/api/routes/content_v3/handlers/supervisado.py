"""Modo Supervisado (DEBT-097) · cola de aprobación por cliente.

GET  /content/supervisado/pending?client_id=...  -> drafts supervisados pendientes.
PATCH /content/supervisado/{content_id}/reject    -> status draft -> rejected.

Approve NO vive aquí: el front reusa PATCH /content/{id}/save (draft->approved dispara
el aprendizaje ARIA ya cableado). Ownership vía accessible_client_ids (RLS-equivalente).
DDD A1/A9: handler -> reader/repo. Gates de cola en supervisado_mode_service.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader, _content_repository as repo
from app.bc_cognition.application import supervisado_mode_service as svc

router = APIRouter()


class SupervisadoToggle(BaseModel):
    client_id: str
    enabled: bool


@router.get("/supervisado/pending")
async def list_pending(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    if client_id not in reader.get_accessible_client_ids(user["id"]):
        raise HTTPException(status_code=403, detail="access_denied")
    drafts = reader.list_content([client_id], "draft", None, 100, 0)
    return {"items": svc.filter_pending(drafts)}


@router.patch("/supervisado/{content_id}/reject")
async def reject_draft(
    content_id: str,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    item = reader.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="content_not_found")
    if str(item.get("client_id")) not in reader.get_accessible_client_ids(user["id"]):
        raise HTTPException(status_code=403, detail="access_denied")
    await repo.safe_insert("reject", repo.update_status, content_id, "rejected")
    return {"id": content_id, "status": "rejected"}


@router.get("/supervisado/settings")
async def get_settings(client_id: str, authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    if client_id not in reader.get_accessible_client_ids(user["id"]):
        raise HTTPException(status_code=403, detail="access_denied")
    return {"enabled": reader.get_requires_approval(client_id)}


@router.patch("/supervisado/settings")
async def set_settings(body: SupervisadoToggle, authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    if body.client_id not in reader.get_accessible_client_ids(user["id"]):
        raise HTTPException(status_code=403, detail="access_denied")
    repo.set_requires_approval(body.client_id, body.enabled)
    return {"enabled": body.enabled}
