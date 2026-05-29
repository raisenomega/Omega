"""Conciencia temporal de ARIA · domain PURO (A2 · sin I/O, sin datetime.now).

`format_now_block`: arma el bloque "hoy es ..." que entra al system como Capa 1 dinámica
(NUNCA persona). `resolve_future_iso`: valida que una fecha sugerida sea ISO futuro válido;
None si no (ausente/basura/pasada) → el puente cae a B2. El determinismo vive AQUÍ (NO
dateparser): `now` SIEMPRE se inyecta para que sea puro y testeable sin tocar el reloj.
"""
from datetime import datetime
from typing import Optional

_DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
          "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def format_now_block(now: datetime, tz_name: str) -> str:
    """Bloque dinámico con el 'ahora' para el system (Capa 1 · NO persona)."""
    dia, mes = _DIAS[now.weekday()], _MESES[now.month - 1]
    return (
        "FECHA Y HORA ACTUAL (usala para calcular fechas relativas como 'mañana' o "
        f"'el viernes'): hoy es {dia} {now.day} de {mes} de {now.year}, "
        f"{now.hour:02d}:{now.minute:02d} ({tz_name})."
    )


def resolve_future_iso(value: Optional[str], now: datetime) -> Optional[str]:
    """Devuelve el ISO sugerido SOLO si parsea a fecha futura válida; si no → None (→ B2)."""
    if not value or not isinstance(value, str):
        return None
    raw = value.strip()
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:  # naive → se interpreta en la tz del 'ahora'
        dt = dt.replace(tzinfo=now.tzinfo)
    return raw if dt > now else None
