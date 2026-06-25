"""Zernio profiles + OAuth connect (B-2 · multi-negocio aislado).

Cada negocio OMEGA = un profile Zernio; getConnectUrl es PROFILE-SCOPED → la cuenta que el
cliente autoriza cae aislada en SU profile (no en una lista global). Reusa _conf del adapter
(misma key + base). Cero fabricacion: non-2xx o sin id → ZernioPublishError honesto (regla G9).
Contrato verificado en vivo (17 jun): POST /profiles → {profile:{_id}} · GET /connect/<plat>?profileId → {authUrl}.
"""
from typing import Optional
from urllib.parse import quote

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


async def find_profile_by_name(name: str) -> Optional[str]:
    """GET /profiles → _id del profile cuyo name == `name` (exact match) · None si no existe.
    Como el name lleva el client_id (PK · B2.5 Capa B), un match exacto es SIEMPRE de ESTE negocio
    (NO cross-tenant · es lo que hace seguro el reuse idempotente)."""
    headers, base = _conf()
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, headers=headers) as client:
        try:
            resp = await client.get(f"{base}/profiles")
        except httpx.HTTPError as e:
            raise ZernioPublishError(f"zernio_transport_error:{type(e).__name__}") from e
    if resp.status_code != 200:
        raise ZernioPublishError(f"zernio_profiles_list_{resp.status_code}:{resp.text[:200]}")
    data = resp.json()
    profiles = data.get("profiles") if isinstance(data, dict) else data
    for p in (profiles or []):
        if p.get("name") == name and p.get("_id"):
            return str(p["_id"])
    return None


async def get_or_create_profile(name: str) -> str:
    """Idempotente (B2.5 Capa B): reusa el profile existente con ESE nombre (único por client_id →
    cierra el huérfano si un create previo no persistió el id) · si no existe, lo crea."""
    existing = await find_profile_by_name(name)
    return existing if existing else await create_profile(name)


async def get_connect_url(platform: str, profile_id: str, redirect_url: Optional[str] = None) -> str:
    """GET /connect/<platform>?profileId(&headless=true&redirectUrl=...) → authUrl del OAuth.
    redirect_url dado → modo HEADLESS: el OAuth vuelve a NUESTRO dominio (B-2 fix · cierra aislamiento +
    white-label). redirect_url None → hosted legacy (retrocompatible · cae en zernio.com)."""
    headers, base = _conf()
    url = f"{base}/connect/{platform}?profileId={profile_id}"
    if redirect_url:
        url += f"&headless=true&redirectUrl={quote(redirect_url, safe='')}"
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
