"""Mapeo ZernioError -> HTTPException honesto (B2.5 Capa A).

Reusable por todos los endpoints Zernio que hoy dejan escapar el error como 500 crudo
(connect-url · fb-pages · etc). Vive en la capa API (importa HTTPException) — la infra
(zernio_profiles/adapter) NUNCA debe importar fastapi. El status real de Zernio viene en el
mensaje `zernio_<ep>_<status>:<body>` (DEBT-ZERNIO-ERROR-STATUSCODE difiere el campo estructurado).
"""
import re

from fastapi import HTTPException

from app.bc_cognition.infrastructure.zernio_adapter import ZernioError, ZernioNotConfigured

_STATUS_RE = re.compile(r"_(\d{3})\b")  # zernio_profiles_400: / zernio_connect_502:


def zernio_error_to_http(exc: ZernioError) -> HTTPException:
    """Traduce un fallo de Zernio a un HTTP legible (jamás 500 crudo).

    - falta la key (ZernioNotConfigured) -> 503 zernio_not_configured.
    - nombre de profile duplicado (Zernio 400 'profile with this name already exists') ->
      409 zernio_profile_name_conflict (accionable para la UI · B2.5).
    - otros 4xx de Zernio -> ese mismo 4xx.
    - transporte/timeout o 5xx -> 502 zernio_unavailable.
    """
    if isinstance(exc, ZernioNotConfigured):
        return HTTPException(status_code=503, detail="zernio_not_configured")
    msg = str(exc)
    if "profile with this name already exists" in msg:
        return HTTPException(status_code=409, detail="zernio_profile_name_conflict")
    status = getattr(exc, "status_code", None)
    if status is None:
        m = _STATUS_RE.search(msg)
        status = int(m.group(1)) if m else None
    transport = bool(getattr(exc, "transport", False)) or msg.startswith("zernio_transport_error")
    if transport or (status is not None and status >= 500):
        return HTTPException(status_code=502, detail="zernio_unavailable")
    if status is not None and 400 <= status < 500:
        return HTTPException(status_code=status, detail=f"zernio_error_{status}")
    return HTTPException(status_code=502, detail="zernio_unavailable")  # malformado/desconocido
