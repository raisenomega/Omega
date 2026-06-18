"""B-2 headless · RETORNO del OAuth de Zernio · el navegador aterriza acá SIN JWT (fix del aislamiento).
Seguridad: el state viene firmado (HMAC · verify_state) → CSRF/forgery guard. Aislamiento: se exige que
el profileId retornado == el zernio_profile_id del negocio. Persistencia: MISMO hardening que zernio-sync
(persist_zernio_account · 422-sin-guardar si la cuenta no está en el profile del negocio).
FB/select-page: GATED (contrato no confirmado) → redirige honesto 'needs_page', NO persiste a ciegas.
"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._zernio_state import verify_state
from app.api.routes.clients_v3.handlers._zernio_persist import persist_zernio_account
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _front_base() -> str:
    """Base del frontend para devolver al usuario al tab de Cuentas (primer CORS origin · fallback vacío)."""
    origins = settings.cors_origins_list
    return origins[0].rstrip("/") if origins else ""


def _back_to_tab(client_id: str, status: str) -> RedirectResponse:
    """Devuelve el navegador al tab de Cuentas del negocio · ?zernio=<status> (el verde lo da Zernio, no esto)."""
    return RedirectResponse(url=f"{_front_base()}/clients?business={client_id}&zernio={status}", status_code=302)


@router.get("/zernio/callback")
async def zernio_callback(st: str = "", profileId: str = "", accountId: str = "",
                          step: str = "") -> RedirectResponse:
    verified = verify_state(st)
    if not verified:
        raise HTTPException(status_code=400, detail="invalid_state")   # firma inválida/forjada
    client_id, platform = verified
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    pid = str(client.get("zernio_profile_id") or "")
    if not pid or pid != profileId:                        # AISLAMIENTO: el retorno debe ser del profile del negocio
        logger.warning("zernio_callback · profileId mismatch · client=%s platform=%s", client_id, platform)
        return _back_to_tab(client_id, "error")
    if step == "select_page":                              # FB · contrato NO confirmado · gated (Commit 3)
        logger.info("zernio_callback · select_page (FB) gated · client=%s", client_id)
        return _back_to_tab(client_id, "needs_page")
    try:
        await persist_zernio_account(client_id, platform, pid, accountId or None)   # hardened · 422 si no en profile
    except HTTPException:
        return _back_to_tab(client_id, "error")            # cuenta no quedó en el profile → no guarda
    return _back_to_tab(client_id, "connected")
