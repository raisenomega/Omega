"""SENTINEL Capa 3 · helpers de chequeo Red/HTTP (headers · TLS · CORS). Aislados del worker (C4)."""
import asyncio
import socket
import ssl
from datetime import datetime, timezone
from typing import Dict, Any

import httpx

# header (lower) → label legible. CSP se chequea aparte (solo aplica al frontend).
EXPECTED_HEADERS = {
    "strict-transport-security": "HSTS",
    "x-frame-options": "X-Frame-Options",
    "x-content-type-options": "X-Content-Type-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}


async def check_headers(url: str, want_csp: bool) -> Dict[str, Any]:
    """GET (sigue redirects) · compara headers presentes vs esperados.

    CSP: acepta enforced O Report-Only como 'presente' · tag csp_mode distingue el modo
    (report-only NO es issue · es el estado deliberado V1 hasta promover a enforced · DEBT-CSP-STRICT).
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as c:
        r = await c.get(url)
    hdr = {k.lower(): v for k, v in r.headers.items()}
    present: Dict[str, str] = {}
    missing = []
    for key, label in EXPECTED_HEADERS.items():
        (present.__setitem__(label, hdr[key]) if key in hdr else missing.append(label))
    csp_mode = None
    if want_csp:
        enforced = hdr.get("content-security-policy")
        report_only = hdr.get("content-security-policy-report-only")
        csp_mode = "enforced" if enforced else "report-only" if report_only else "missing"
        if csp_mode == "missing":
            missing.append("Content-Security-Policy")
        else:
            present["Content-Security-Policy"] = (enforced or report_only)[:120]
    return {"final_url": str(r.url), "present": present, "missing": missing, "csp_mode": csp_mode}


def _tls_sync(host: str, port: int = 443) -> Dict[str, Any]:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=15) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert() or {}
            version = ssock.version()
    expires = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    return {
        "version": version,
        "cert_subject": dict(x[0] for x in cert.get("subject", ())).get("commonName"),
        "cert_issuer": dict(x[0] for x in cert.get("issuer", ())).get("organizationName"),
        "cert_expires_at": expires.isoformat(),
        "days_until_expiry": (expires - datetime.now(timezone.utc)).days,
    }


async def check_tls(host: str) -> Dict[str, Any]:
    try:
        return await asyncio.to_thread(_tls_sync, host)
    except Exception as e:  # noqa: BLE001 — best-effort, el error es el dato
        return {"error": str(e)}


async def check_cors(api_url: str) -> Dict[str, Any]:
    """OPTIONS con Origin no confiable · si lo refleja en ACAO o usa '*' → CORS débil."""
    evil = "https://evil.example.com"
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.options(api_url, headers={"Origin": evil, "Access-Control-Request-Method": "GET"})
        acao = r.headers.get("access-control-allow-origin")
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    return {"evil_origin_acao": acao, "wildcard_detected": acao == "*", "reflects_untrusted": acao == evil}
