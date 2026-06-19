# TEMP · DEBT-ZERNIO-CAPTURE-ENDPOINT-TEMP · REMOVER tras capturar el contrato headless (FB · paso 0).
# Endpoint efímero de captura del retorno OAuth headless de Zernio (experimento controlado · platform-agnóstico).
# NO persiste nada en DB. Protegido por token de UN SOLO USO en la URL (?cap=). Sin ZERNIO_CAPTURE_TOKEN
# en el entorno → inerte (403). REDACCIÓN: code/tempToken JAMÁS completos en logs (solo presencia/len);
# el valor completo solo en el HTML efímero que el owner copia. Quitar (archivo + línea en main.py) al terminar.
import hmac
import html
import logging
import os
import time

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# claves cuyo VALOR es credencial OAuth → nunca completas en logs
_SENSITIVE = {"code", "temptoken", "token", "connect_token", "access_token"}
# single-use en memoria (Railway --workers 1 → estado en proceso OK). token consumido → 410.
_consumed: dict[str, float] = {}
_TTL_SECONDS = 1800.0  # ventana máxima de validez del token desde el primer hit


def _valid_token(cap: str) -> bool:
    """Compara cap contra ZERNIO_CAPTURE_TOKEN (constante en tiempo). Env vacío → siempre falso (inerte)."""
    expected = (os.getenv("ZERNIO_CAPTURE_TOKEN") or "").strip()
    return bool(expected) and bool(cap) and hmac.compare_digest(cap, expected)


def _redact(key: str, value: str) -> str:
    """Para LOGS: sensibles → solo presencia + longitud (nunca el valor); resto → truncado."""
    if key.lower() in _SENSITIVE:
        return f"<present len={len(value)}>"
    return value[:80]


def _row(key: str, value: str) -> str:
    """Para PANTALLA (efímero): valor COMPLETO, escapado para evitar reflexión XSS."""
    return f"<tr><td><b>{html.escape(key)}</b></td><td><code>{html.escape(value)}</code></td></tr>"


@router.get("/zernio-experiment/capture", response_class=HTMLResponse)
async def zernio_capture(request: Request, cap: str = "") -> HTMLResponse:
    """Aterrizaje del retorno headless de Zernio. Valida token single-use, loguea redactado,
    muestra TODOS los params en pantalla (efímero). TEMP · remover tras capturar el contrato."""
    if not _valid_token(cap):
        logger.warning("zernio_capture · token inválido/ausente → 403")
        return HTMLResponse("<h3>403 · token de captura inválido o ausente</h3>", status_code=403)
    now = time.time()
    if cap in _consumed:
        logger.warning("zernio_capture · token ya consumido → 410")
        return HTMLResponse("<h3>410 · token ya usado (single-use)</h3>", status_code=410)
    _consumed[cap] = now

    params = {k: v for k, v in request.query_params.items() if k != "cap"}
    redacted = {k: _redact(k, v) for k, v in params.items()}
    logger.info(
        "zernio_capture · callback HEADLESS recibido · keys=%s · redacted=%s",
        sorted(params.keys()), redacted,
    )
    rows = "".join(_row(k, v) for k, v in params.items()) or "<tr><td colspan=2>(sin params)</td></tr>"
    body = (
        "<html><head><meta charset='utf-8'><title>Zernio capture</title></head><body>"
        "<h2>Retorno HEADLESS de Zernio capturado (efímero)</h2>"
        f"<p>host destino = <code>{html.escape(str(request.url.hostname or ''))}</code> "
        "(confirma que el aterrizaje es en NUESTRO dominio, no zernio.com)</p>"
        "<table border=1 cellpadding=6>" + rows + "</table>"
        "<p>Copiá/screenshoteá estos valores. El endpoint es de un solo uso y se remueve al terminar.</p>"
        "</body></html>"
    )
    return HTMLResponse(body, status_code=200)
