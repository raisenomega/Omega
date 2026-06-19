"""B-2 FB headless · Paso 3 · endpoints del page-picker (JWT). Recuperan el pending stasheado por
(user_id, client_id, platform). DEFENSA-EN-PROFUNDIDAD: get_pending va keyed por el user_id del JWT →
si quien llama NO inició el flujo, la key no matchea → None → 409 (no entrega tokens · ni revela que
exista un pending de otro). Los tokens NUNCA salen al cliente (solo {id,name} de páginas). clear_pending
tras el select (éxito O fallo · un intento no deja el stash vivo para reintento)."""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.clients_v3.handlers.zernio_oauth import _owned
from app.api.routes.clients_v3.handlers._zernio_pending import get_pending, clear_pending
from app.api.routes.clients_v3.handlers._zernio_persist import persist_zernio_account
from app.bc_cognition.infrastructure.zernio_facebook import get_facebook_pages, select_facebook_page

router = APIRouter()
_FB = "facebook"


class SelectPageRequest(BaseModel):
    page_id: str


@router.get("/{client_id}/social-accounts/facebook/pending-pages")
async def fb_pending_pages(client_id: str, authorization: Optional[str] = Header(None)) -> dict:
    user, client = await _owned(client_id, authorization)         # JWT + ownership
    pid = str(client.get("zernio_profile_id") or "")             # Zernio EXIGE profileId en get-facebook-pages
    if not pid:
        raise HTTPException(status_code=409, detail="zernio_profile_missing")
    pending = get_pending(str(user["id"]), client_id, _FB)        # keyed por user_id firmado → ata al iniciador
    if not pending:
        raise HTTPException(status_code=409, detail="no_pending_facebook_oauth")   # expirado/ajeno/inexistente
    temp_token, connect_token = pending
    pages = await get_facebook_pages(temp_token, connect_token, pid)   # tokens NUNCA al cliente · solo {id,name}
    return {"pages": [{"id": p.get("id"), "name": p.get("name")} for p in pages]}


@router.post("/{client_id}/social-accounts/facebook/select-page")
async def fb_select_page(client_id: str, body: SelectPageRequest,
                         authorization: Optional[str] = Header(None)) -> dict:
    user, client = await _owned(client_id, authorization)
    pid = str(client.get("zernio_profile_id") or "")
    if not pid:
        raise HTTPException(status_code=409, detail="zernio_profile_missing")
    pending = get_pending(str(user["id"]), client_id, _FB)
    if not pending:
        raise HTTPException(status_code=409, detail="no_pending_facebook_oauth")
    temp_token, connect_token = pending
    try:
        aid = await select_facebook_page(temp_token, connect_token, body.page_id, pid)
        result = await persist_zernio_account(client_id, _FB, pid, aid)   # hardened · 422 si no quedó en el profile
    finally:
        clear_pending(str(user["id"]), client_id, _FB)           # éxito O fallo → no deja el stash vivo
    return {"ok": True, **result}
