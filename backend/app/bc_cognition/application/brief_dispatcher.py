"""Brief dispatcher (DEBT-105) · briefs periódicos al owner por email vía Resend.

AISLADO a propósito de alert_dispatcher.py (path de alarma probado E2E · en prod
desde 25 may · NO se toca). Duplica el POST a Resend deliberadamente: si un brief
falla, la alarma sigue viva. Best-effort: ningún fallo rompe el cron. Sin SDK · httpx.
"""
import logging
import httpx
from typing import Any
from app.config import settings
from app.bc_cognition.application._brief_formatters import format_sentinel, format_oracle
from app.bc_cognition.infrastructure.hermes_usage import record_mcp_use  # HERMES f1.5 · usage-tracking

logger = logging.getLogger(__name__)

_RESEND_URL = "https://api.resend.com/emails"
_TIMEOUT = 8.0


async def _post_resend(subject: str, text: str) -> bool:
    """POST best-effort a Resend. Sin key -> skip. Cualquier error -> False (no propaga)."""
    if not settings.resend_api_key:
        logger.warning("brief · RESEND_API_KEY ausente -> email skip")
        return False
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
            resp = await c.post(_RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json={"from": settings.alert_email_from, "to": [settings.alert_email_to],
                      "subject": subject, "text": text})
            resp.raise_for_status()
        record_mcp_use("resend", ok=True)  # HERMES f1.5
        return True
    except Exception as e:
        record_mcp_use("resend", ok=False, detail=str(e)[:80])  # HERMES f1.5
        logger.error(f"brief · Resend fallo: {e}")
        return False


async def dispatch_sentinel_brief(result: dict[str, Any]) -> bool:
    """Envía el brief diario de SENTINEL al owner (best-effort)."""
    return await _post_resend(*format_sentinel(result))


async def dispatch_oracle_brief(brief: dict[str, Any]) -> bool:
    """Envía el brief semanal de ORACLE al owner (best-effort)."""
    return await _post_resend(*format_oracle(brief))


async def dispatch_aria_learning_brief(report: dict[str, Any]) -> bool:
    """Envía el ARIA Learning Report al owner (DEBT-101 · False si sin actividad → caller skip)."""
    from app.bc_cognition.application._aria_learning_formatter import format_aria_learning
    formatted = format_aria_learning(report)
    if not formatted:
        return False
    return await _post_resend(*formatted)
