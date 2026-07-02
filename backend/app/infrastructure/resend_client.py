"""Envío de email vía Resend con surfacing HONESTO del error (a diferencia de alert/brief dispatcher
que son best-effort y tragan el fallo). Devuelve (ok, error_detail) · el caller decide el HTTP.
Sin API key → not_configured. Resend rechaza (403 dominio no verificado con onboarding@resend.dev,
etc.) → el detalle real vuelve al owner · JAMÁS se reporta éxito falso."""
import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)
_URL = "https://api.resend.com/emails"
_TIMEOUT = 10.0


async def send_email(to: str, subject: str, text: str) -> tuple[bool, str | None]:
    if not settings.resend_api_key:
        return False, "not_configured"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
            resp = await c.post(
                _URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={"from": settings.alert_email_from, "to": [to], "subject": subject, "text": text},
            )
        if resp.status_code >= 400:
            detail = resp.text[:200]
            logger.warning(f"resend rechazó ({resp.status_code}): {detail}")
            return False, detail
        return True, None
    except Exception as e:
        logger.error(f"resend error: {e}")
        return False, str(e)[:200]
