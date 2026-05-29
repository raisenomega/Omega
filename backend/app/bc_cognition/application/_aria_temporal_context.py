"""Borde impuro de la conciencia temporal de ARIA (application).

Resuelve la timezone del cliente y el 'ahora' real, y delega el formateo/validación al
domain puro (`aria_temporal`). tz NULL/inválida → fallback `America/Puerto_Rico` + log
(NUNCA negar agendado por tz faltante · decisión owner)."""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.bc_cognition.domain.aria_temporal import format_now_block

logger = logging.getLogger(__name__)

_DEFAULT_TZ = "America/Puerto_Rico"  # convención del repo (onboarding_extra, scheduler)


def resolve_tz(tz_str):
    """(ZoneInfo, nombre) · NULL/inválida → fallback PR + warning, sin bloquear."""
    if tz_str:
        try:
            return ZoneInfo(tz_str), tz_str
        except (ZoneInfoNotFoundError, ValueError):
            logger.warning("ARIA tz inválida '%s' → fallback %s", tz_str, _DEFAULT_TZ)
    else:
        logger.warning("ARIA sin timezone de cliente → fallback %s", _DEFAULT_TZ)
    return ZoneInfo(_DEFAULT_TZ), _DEFAULT_TZ


def now_for(tz_str) -> datetime:
    """El 'ahora' real en la tz resuelta (para validar fechas futuras)."""
    tz, _ = resolve_tz(tz_str)
    return datetime.now(tz)


def build_time_block(tz_str) -> str:
    """Bloque dinámico 'hoy es ...' que se inyecta al system de ARIA (Capa 1)."""
    tz, name = resolve_tz(tz_str)
    return format_now_block(datetime.now(tz), name)
