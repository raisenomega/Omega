"""PATCH /content/{id}/draft · editar caption (generated_text) y/o fecha (metadata.fecha_sugerida)
de un draft supervisado. SOLO status='draft' (audit B4). P1: edicion explicita del cliente.

Cableados: #1 fecha re-validada con resolve_future_iso(now_for(client_tz)) · #2 metadata por MERGE
(preserva supervisado/platform/origen) · #3 tz de client_context · #4 write en _content_repository.
Semantica del body: campo ausente = no tocar · scheduled_for=null = borrar fecha (vuelve a B2 · no agenda).
NO usa safe_insert: el write ES la accion primaria · si falla → 500 → la UI muestra error (no miente)."""
import asyncio
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader, _content_repository as repo
from app.bc_cognition.domain.aria_temporal import resolve_future_iso
from app.bc_cognition.application._aria_temporal_context import now_for

router = APIRouter()


class EditDraftRequest(BaseModel):
    generated_text: Optional[str] = None
    scheduled_for: Optional[str] = None  # ausente=no tocar · null=borrar · ISO=set


@router.patch("/{content_id}/draft")
async def edit_draft(content_id: str, request: EditDraftRequest,
                     authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    item = reader.get_content_item(content_id)
    if not item:
        raise HTTPException(status_code=404, detail="content_not_found")
    client_id = str(item.get("client_id") or "")
    if client_id not in reader.get_accessible_client_ids(user["id"]):
        raise HTTPException(status_code=403, detail="access_denied")
    if item.get("status") != "draft":
        raise HTTPException(status_code=409, detail="not_editable_unless_draft")

    fields = request.model_fields_set
    new_text = request.generated_text if "generated_text" in fields else None
    if new_text is not None and not new_text.strip():
        raise HTTPException(status_code=400, detail="empty_caption")

    new_meta = None
    if "scheduled_for" in fields:
        meta = dict(item.get("metadata") or {})  # #2 MERGE: parte del estado vivo
        if request.scheduled_for is None:
            meta.pop("fecha_sugerida", None)      # null → B2 (no agenda)
        else:
            iso = resolve_future_iso(request.scheduled_for, now_for(reader.get_client_timezone(client_id)))  # #1 #3
            if iso is None:
                raise HTTPException(status_code=422, detail="invalid_or_past_date")
            meta["fecha_sugerida"] = iso
        new_meta = meta

    if new_text is None and new_meta is None:
        raise HTTPException(status_code=400, detail="nothing_to_update")

    await asyncio.to_thread(repo.update_draft_fields, content_id, new_text, new_meta)
    return {"id": content_id,
            "generated_text": new_text if new_text is not None else item.get("generated_text"),
            "scheduled_for": (new_meta if new_meta is not None else item.get("metadata") or {}).get("fecha_sugerida")}
