"""B-2 headless · RETORNO del OAuth de Zernio · el navegador aterriza acá SIN JWT (fix del aislamiento).
Seguridad: el state viene firmado (HMAC · verify_state) → CSRF/forgery guard. Aislamiento: se exige que
el profileId retornado == el zernio_profile_id del negocio. Persistencia: MISMO hardening que zernio-sync
(persist_zernio_account · 422-sin-guardar si la cuenta no está en el profile del negocio).
FB/select-page: GATED (contrato no confirmado) → redirige honesto 'needs_page', NO persiste a ciegas.
"""
import json
import logging
from typing import Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._zernio_state import verify_state
from app.api.routes.clients_v3.handlers._zernio_persist import persist_zernio_account
from app.api.routes.clients_v3.handlers._zernio_pending import stash_pending
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _parse_user_profile(raw: str) -> Optional[dict]:
    """userProfile del redirect FB = JSON doble-url-encoded · requerido por el POST select-page. Parseo
    DEFENSIVO: input externo malformado/ausente NO crashea el callback (500 opaco) → None (el endpoint
    select decide · LISTAR no lo necesita, solo profileId+tempToken). NUNCA loguea el valor (nombre/foto = PII)."""
    if not raw:
        return None
    try:
        parsed = json.loads(unquote(raw))
        return parsed if isinstance(parsed, dict) else None
    except (ValueError, TypeError):
        logger.warning("zernio_callback · userProfile ilegible (no parsea) → degrada honesto")
        return None


def _front_base(origin: str) -> str:
    """Vuelve al MISMO origen del usuario (firmado en el state) SOLO si está en la allowlist
    (anti open-redirect · NUNCA a un origen arbitrario aunque venga firmado). Si no permitido/ausente
    → primer origen permitido. Resuelve www vs non-www sin depender del orden de la lista."""
    allowed = settings.cors_origins_list
    if origin and origin in allowed:
        return origin.rstrip("/")
    return allowed[0].rstrip("/") if allowed else ""


def _back_to_tab(status: str, platform: str, origin: str = "") -> RedirectResponse:
    """Aterriza el POPUP en /zernio/return (relay · ?zernio=<status>&platform). Ese relay sólo dispara un
    refetch en el opener; el verde lo da connected-accounts (verdad de Zernio), no este redirect ni el postMessage."""
    return RedirectResponse(url=f"{_front_base(origin)}/zernio/return?zernio={status}&platform={platform}",
                            status_code=302)


@router.get("/zernio/callback")
async def zernio_callback(st: str = "", profileId: str = "", accountId: str = "", step: str = "",
                          tempToken: str = "", connect_token: str = "", userProfile: str = "") -> RedirectResponse:
    verified = verify_state(st)
    if not verified:
        raise HTTPException(status_code=400, detail="invalid_state")   # firma inválida/forjada
    client_id, platform, origin, user_id = verified                    # user_id+origin firmados (HMAC · inforjables)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    pid = str(client.get("zernio_profile_id") or "")
    if not pid or pid != profileId:                        # AISLAMIENTO: el retorno debe ser del profile del negocio
        logger.warning("zernio_callback · profileId mismatch · client=%s platform=%s", client_id, platform)
        return _back_to_tab("error", platform, origin)
    if step == "select_page":                              # FB · stash server-side + handoff al page-picker
        if not user_id:                                    # anómalo en FB (no hay states FB legacy legítimos) → no stashea
            logger.warning("zernio_callback · select_page sin user_id firmado → no stashea · client=%s", client_id)
            return _back_to_tab("needs_page", platform, origin)
        profile = _parse_user_profile(userProfile)                     # defensivo: malformado/ausente → None
        stash_pending(user_id, client_id, platform, tempToken, connect_token, profile)   # keyed por user_id · server-side
        logger.info("zernio_callback · select_page (FB) · pending stasheado · client=%s · userProfile=%s",
                    client_id, "ok" if profile else "ausente/ilegible")   # NUNCA el valor (PII)
        return _back_to_tab("needs_page", platform, origin)            # redirect SIN tokens en la URL
    try:
        await persist_zernio_account(client_id, platform, pid, accountId or None)   # hardened · 422 si no en profile
    except HTTPException:
        return _back_to_tab("error", platform, origin)            # cuenta no quedó en el profile → no guarda
    return _back_to_tab("connected", platform, origin)
