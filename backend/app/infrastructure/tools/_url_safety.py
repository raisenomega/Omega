# backend/app/infrastructure/tools/_url_safety.py
# SSRF defense in depth — DEBT-075
# Pure stdlib (ipaddress + socket). Compartido por _web_scraper y fetch_url_tool.

from __future__ import annotations
import ipaddress
import socket
from urllib.parse import urlparse


def _ip_is_public(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """False si la IP cae en un rango interno/peligroso (loopback, link-local,
    privada RFC1918, ULA IPv6 fc00::/7, no-especificada, reservada)."""
    if (
        ip.is_loopback          # 127.0.0.0/8, ::1
        or ip.is_link_local     # 169.254.0.0/16 (incl. 169.254.169.254 metadata)
        or ip.is_private        # 10/8, 172.16/12, 192.168/16, fc00::/7
        or ip.is_unspecified    # 0.0.0.0, ::
        or ip.is_reserved
        or ip.is_multicast
    ):
        return False
    return True


def _resolve_hosts(host: str) -> list[str]:
    """Resuelve host → lista de IPs (str). Lanza si DNS falla (host inválido)."""
    infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    return [info[4][0] for info in infos]


def is_public_host(url: str) -> bool:
    """True solo si TODAS las IPs resueltas del host son públicas.

    Defensa SSRF en profundidad: rechaza loopback, link-local (metadata cloud),
    rangos privados RFC1918, ULA IPv6 y reservados. Resuelve DNS y valida cada IP
    (mitiga DNS-rebinding en el momento del chequeo). Cualquier fallo => False
    (fail-safe: ante duda, no se permite el fetch).
    """
    try:
        host = (urlparse(url).hostname or "").strip()
    except Exception:
        return False
    if not host:
        return False

    # IP literal: validar directo, sin DNS.
    try:
        return _ip_is_public(ipaddress.ip_address(host))
    except ValueError:
        pass  # no es IP literal → resolver por DNS

    try:
        ips = _resolve_hosts(host)
    except Exception:
        return False
    if not ips:
        return False
    for ip_str in ips:
        try:
            if not _ip_is_public(ipaddress.ip_address(ip_str)):
                return False
        except ValueError:
            return False
    return True
