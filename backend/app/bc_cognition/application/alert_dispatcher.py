"""Alert dispatcher SENTINEL · notifica score bajo por Email (Resend · activo) + Telegram (opcional).

dispatch_sentinel_alert: best-effort · ningún fallo de notificación rompe el scan (try/except → log).
Email vía Resend si settings.resend_api_key. Telegram solo si telegram_bot_token + telegram_chat_id →
se activa al pegar el token en Railway (el restart re-lee settings · sin code deploy). Sin SDK · httpx.
"""
import logging
import httpx
from typing import Any
from app.config import settings

logger = logging.getLogger(__name__)

_RESEND_URL = "https://api.resend.com/emails"
_TIMEOUT = 8.0


def _format_body(score: int, issues: list[dict[str, Any]], timestamp: str) -> str:
    crit = sum(1 for i in issues if i.get("severity") == "CRITICAL")
    lines = [f"· [{i.get('severity', '?')}] {i.get('message') or i.get('title') or i.get('agent_code') or 'issue'}"
             for i in issues[:15]]
    detail = "\n".join(lines) if lines else "· (sin detalle de issues)"
    return (f"SENTINEL · score {score}/100 (umbral 80) · {timestamp}\n"
            f"{len(issues)} issues · {crit} CRITICAL\n\n{detail}")


async def dispatch_sentinel_alert(score: int, issues: list[dict[str, Any]], timestamp: str) -> dict[str, bool]:
    """Despacha alerta de score bajo. Retorna {email, telegram} (True = enviado)."""
    body = _format_body(score, issues, timestamp)
    return {"email": await _send_resend(body, score), "telegram": await _send_telegram(body)}


async def _send_resend(body: str, score: int) -> bool:
    if not settings.resend_api_key:
        logger.warning("alert · RESEND_API_KEY ausente → email skip")
        return False
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
            resp = await c.post(_RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={"from": settings.alert_email_from, "to": [settings.alert_email_to],
                      "subject": f"🛡️ SENTINEL · score {score}/100 (<80)", "text": body})
            resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"alert · Resend falló: {e}")
        return False


async def _send_telegram(body: str) -> bool:
    token, chat = settings.telegram_bot_token, settings.telegram_chat_id
    if not (token and chat):  # preparado · activa al pegar TELEGRAM_BOT_TOKEN + CHAT_ID en Railway
        return False
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
            resp = await c.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                json={"chat_id": chat, "text": body})
            resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"alert · Telegram falló: {e}")
        return False
