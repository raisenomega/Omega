"""Cadencia de estrategias por nivel ARIA · domain PURO (A2 · sin I/O).

Dato de DEBT-096 (spec §5/§6): CUÁNTAS estrategias por periodo según nivel. Fase 1 genera
on-demand (tipo 'manual'); Fase 2 (cron) consultará `cadence_for` para la cadencia automática
(semanal/3x/diaria) — la lógica del dato vive AQUÍ, el cron solo la dispara.
"""
from typing import Optional

# nivel ARIA → tipo de cadencia auto (None = ese nivel no genera estrategias automáticas).
_CADENCE_BY_LEVEL: dict[int, Optional[str]] = {1: None, 2: "semanal", 3: "tres_semana", 4: "diaria"}


def cadence_for(level: int) -> Optional[str]:
    """Tipo de cadencia automática para el nivel ARIA · None si no aplica (ARIA 1)."""
    return _CADENCE_BY_LEVEL.get(level)


# weekday: lunes=0 … domingo=6 (datetime.weekday()). Traduce la cadencia a días de corrida del cron.
def should_generate_on(level: int, weekday: int) -> bool:
    """¿El cron debe generar HOY para este nivel? · domain puro (testeable sin reloj)."""
    cadence = cadence_for(level)
    if cadence == "diaria":       # ARIA 4 · todos los días
        return True
    if cadence == "tres_semana":  # ARIA 3 · L/M/V (días de mayor actividad en redes · decisión de producto)
        return weekday in (0, 2, 4)
    if cadence == "semanal":      # ARIA 2 · lunes
        return weekday == 0
    return False                  # ARIA 1 (None) · sin generación automática
