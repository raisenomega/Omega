"""GUARDIAN geo · lookup IP→ubicación vía IPinfo (httpx directo · sin SDK · cero dep nueva).

Fail-open (P4): si el lookup falla o la IP es privada/inválida → (None, ...) y el login NO se bloquea.
Token opcional: settings.ipinfo_token (50k/mo) · ausente = tokenless (~1k/día, campos básicos).
"""
import ipaddress
import logging
from dataclasses import dataclass
from typing import Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeoData:
    country: Optional[str]   # ISO-2 (ej. "AR", "US") · IPinfo no devuelve nombre full
    region: Optional[str]
    city: Optional[str]
    timezone: Optional[str]
    loc: Optional[str]       # "lat,lon"
    org: Optional[str]       # ASN / ISP


@dataclass(frozen=True)
class GeoError:
    code: str
    detail: str


def _is_private(ip: str) -> bool:
    """IP privada/loopback/link-local/inválida → True (no se hace lookup externo)."""
    try:
        a = ipaddress.ip_address(ip)
        return a.is_private or a.is_loopback or a.is_link_local or a.is_reserved
    except ValueError:
        return True


def lookup_ip_geo(ip_address: str) -> Tuple[Optional[GeoData], Optional[GeoError]]:
    """IP pública → GeoData. Privada/inválida → (None, None). Falla → (None, GeoError). Cero raise."""
    if not ip_address or _is_private(ip_address):
        return None, None
    params = {"token": settings.ipinfo_token} if settings.ipinfo_token else {}
    try:
        r = httpx.get(f"https://ipinfo.io/{ip_address}/json", params=params, timeout=4.0)
    except Exception as e:  # noqa: BLE001 — fail-open: red caída no bloquea login
        logger.warning(f"geo lookup error {ip_address}: {e}")
        return None, GeoError("lookup_failure", str(e)[:80])
    if r.status_code != 200:
        return None, GeoError("http_error", f"ipinfo status {r.status_code}")
    d = r.json()
    if d.get("bogon"):  # IPinfo marca IPs no enrutables
        return None, None
    return GeoData(
        country=d.get("country"), region=d.get("region"), city=d.get("city"),
        timezone=d.get("timezone"), loc=d.get("loc"), org=d.get("org"),
    ), None
