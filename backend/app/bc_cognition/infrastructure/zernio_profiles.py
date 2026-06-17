"""Zernio profiles + OAuth connect (B-2 · multi-negocio aislado).

Cada negocio OMEGA = un profile Zernio; getConnectUrl es PROFILE-SCOPED → la cuenta que el
cliente autoriza cae aislada en SU profile (no en una lista global). Reusa _conf del adapter
(misma key + base). Cero fabricacion: non-2xx o sin id → ZernioPublishError honesto (regla G9).
Contrato verificado en vivo (17 jun): POST /profiles → {profile:{_id}} · GET /connect/<plat>?profileId → {authUrl}.
"""
import httpx

from app.bc_cognition.infrastructure.zernio_adapter import _conf, ZernioPublishError, _HTTP_TIMEOUT


async def create_profile(name: str, description: str = "") -> str:
    """POST /profiles → devuelve profile._id (el zernio_profile_id del negocio)."""
    headers, base = _conf()
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.post(f"{base}/profiles", json={"name": name, "description": description})
        except httpx.HTTPError as e:
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code not in (200, 201):
        raise ZernioPublishError(f"zernio_profiles_{resp.status_code}:{resp.text[:200]}")
    pid = (resp.json().get("profile") or {}).get("_id")
    if not pid:
        raise ZernioPublishError("zernio_no_profile_id")
    return str(pid)


async def get_connect_url(platform: str, profile_id: str) -> str:
    """GET /connect/<platform>?profileId → authUrl del OAuth hosteado (cae en el profile del negocio)."""
    headers, base = _conf()
    url = f"{base}/connect/{platform}?profileId={profile_id}"
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.get(url)
        except httpx.HTTPError as e:
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code != 200:
        raise ZernioPublishError(f"zernio_connect_{resp.status_code}:{resp.text[:200]}")
    auth = resp.json().get("authUrl")
    if not auth:
        raise ZernioPublishError("zernio_no_auth_url")
    return str(auth)
