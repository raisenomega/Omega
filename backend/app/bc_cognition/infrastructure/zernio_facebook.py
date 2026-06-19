"""Adapter Zernio · page-selection de Facebook (B-2 headless · branch FB · contrato capturado 18 jun).
Tras el OAuth FB, Zernio devuelve step=select_page + tempToken + connect_token: las paginas otorgadas en el
consent de Meta se LISTAN y se SELECCIONA una para adjuntarla al profile del negocio. connect_token =
security scheme 'connectToken' de Zernio → header X-Connect-Token; tempToken = id de la sesion OAuth
pendiente. Cero-fabricacion (patron espejo de zernio_adapter): non-2xx/transporte → ZernioPublishError
TIPADO, JAMAS un fallback silencioso (lista vacia = 'Zernio dice 0 paginas', distinto de un fallo). Tokens
NUNCA completos en logs (solo presencia/len). WIRING centralizado en _with_connect_token + _fb_session_params
(UN solo punto de cambio · se confirma en el E2E del paso 5)."""
import logging

import httpx

from app.bc_cognition.infrastructure.zernio_adapter import _conf, ZernioPublishError, _HTTP_TIMEOUT

logger = logging.getLogger(__name__)


def _tok(token: str) -> str:
    """Para logs: SOLO presencia + longitud · NUNCA el valor (connect_token/tempToken son credenciales)."""
    return f"<present len={len(token)}>" if token else "<absent>"


def _with_connect_token(headers: dict, connect_token: str) -> dict:
    """WIRING (1 de 2): connect_token → header X-Connect-Token (security scheme 'connectToken' de Zernio).
    Si el E2E (paso 5) revela otro nombre de header, se ajusta SOLO acá."""
    if connect_token:
        headers["X-Connect-Token"] = connect_token
    return headers


_FB_SELECT_PATH = "/connect/facebook/select-page"   # GET lista · POST elige (OpenAPI Zernio · unico path real)


def _fb_session_params(temp_token: str, profile_id: str) -> dict:
    """WIRING (2 de 2): params de sesion del select-page (contrato OpenAPI real). profileId = profile
    Zernio del negocio; tempToken = access token temporal del callback OAuth (Zernio lo nombra 'tempToken',
    NO 'accountId'). UN solo punto: ajuste de contrato = 1 linea aca."""
    return {"profileId": profile_id, "tempToken": temp_token}


async def get_facebook_pages(temp_token: str, connect_token: str, profile_id: str) -> list[dict]:
    """GET /connect/facebook/select-page → paginas FB que el user administra (a elegir). Lista (puede ser
    vacia = 0 paginas reales · NO es error). non-2xx/transporte → ZernioPublishError (jamas [] enmascarando)."""
    headers, base = _conf()
    headers = _with_connect_token(headers, connect_token)
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.get(f"{base}{_FB_SELECT_PATH}", params=_fb_session_params(temp_token, profile_id))
        except httpx.HTTPError as e:
            logger.warning("get_facebook_pages transporte · ct=%s tt=%s", _tok(connect_token), _tok(temp_token))
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code != 200:
        raise ZernioPublishError(f"zernio_fb_pages_{resp.status_code}:{resp.text[:200]}")
    return resp.json().get("pages", [])


async def select_facebook_page(temp_token: str, connect_token: str, page_id: str,
                               profile_id: str, user_profile: dict) -> str:
    """POST /connect/facebook/select-page {profileId, pageId, tempToken, userProfile} → adjunta la pagina
    al profile. Devuelve account.accountId. non-2xx/sin-id → ZernioPublishError (cero-fabricacion)."""
    headers, base = _conf()
    headers = _with_connect_token(headers, connect_token)
    body = {**_fb_session_params(temp_token, profile_id), "pageId": page_id, "userProfile": user_profile}
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.post(f"{base}{_FB_SELECT_PATH}", json=body)
        except httpx.HTTPError as e:
            logger.warning("select_facebook_page transporte · ct=%s tt=%s", _tok(connect_token), _tok(temp_token))
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code not in (200, 201):
        raise ZernioPublishError(f"zernio_fb_select_{resp.status_code}:{resp.text[:200]}")
    aid = (resp.json().get("account") or {}).get("accountId")   # contrato real: account.accountId (no _id)
    if not aid:
        raise ZernioPublishError("zernio_fb_no_account_id")
    return str(aid)
