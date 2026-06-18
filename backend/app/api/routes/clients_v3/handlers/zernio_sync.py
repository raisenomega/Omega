"""B-2 · zernio-sync · captura manual ('Verificar conexión') del binding, CON HARDENING anti-cross-publish.
Fallback del flujo headless (zernio_callback): si el redirect se perdió, el owner re-sincroniza acá.
La persistencia hardened vive en _zernio_persist.persist_zernio_account (compartida con el callback):
lee SOLO el profile del negocio, re-valida pertenencia, handle autoritativo de Zernio, 422-sin-guardar.
SEGURIDAD: service_role BYPASSA RLS → user_owns_client ANTES de tocar nada.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3.handlers._zernio_persist import persist_zernio_account

router = APIRouter()


@router.post("/{client_id}/social-accounts/{platform}/zernio-sync")
async def zernio_sync(client_id: str, platform: str,
                      authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):          # OWNERSHIP GUARD
        raise HTTPException(status_code=403, detail="client_access_denied")
    pid = client.get("zernio_profile_id")
    if not pid:
        raise HTTPException(status_code=409, detail="zernio_profile_missing")
    result = await persist_zernio_account(client_id, platform, str(pid))   # hardened · 422 si no en profile
    return {"ok": True, **result}
