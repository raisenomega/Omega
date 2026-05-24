"""Timestamp spacer · DEBT-CL-018 bulk schedule.

Función pura · cero imports externos · self-checks al import (patrón
limits_omega.py / video_entitlements.py).

Reparte N posts respetando LIMITS_OMEGA:
  MIN_HORAS_ENTRE_POSTS = 2 (anti-spam · plataformas penalizan ráfaga)
  MAX_POSTS_AUTO_PER_DIA_CLIENTE = 3 (saturación de feed)

Diseño: next-day rows usan la MISMA hora-base que el primer post
(consistencia cross-día · predecible para el usuario).
"""
from datetime import datetime, timedelta
from typing import List

HOURS_BETWEEN = 2
MAX_PER_DAY = 3


def space_timestamps(base: datetime, n: int) -> List[datetime]:
    """N timestamps · 2h gap intra-día · 3 max/día · overflow día siguiente.

    Ejemplo: base=2026-05-24T10:00, n=5
      → [10:00 d24, 12:00 d24, 14:00 d24, 10:00 d25, 12:00 d25]
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    base_clean = base.replace(microsecond=0)
    out: List[datetime] = []
    for i in range(n):
        day_offset = i // MAX_PER_DAY
        in_day = i % MAX_PER_DAY
        ts = base_clean + timedelta(days=day_offset, hours=in_day * HOURS_BETWEEN)
        out.append(ts)
    return out


# Self-checks al import (fail-fast · sin pytest infra)
_t5 = space_timestamps(datetime(2026, 5, 24, 10, 0, 0), 5)
assert len(_t5) == 5
assert _t5[0] == datetime(2026, 5, 24, 10, 0, 0)
assert _t5[1] == datetime(2026, 5, 24, 12, 0, 0)
assert _t5[2] == datetime(2026, 5, 24, 14, 0, 0)
assert _t5[3] == datetime(2026, 5, 25, 10, 0, 0)
assert _t5[4] == datetime(2026, 5, 25, 12, 0, 0)
_t1 = space_timestamps(datetime(2026, 1, 1, 8, 0, 0), 1)
assert _t1 == [datetime(2026, 1, 1, 8, 0, 0)]
_t10 = space_timestamps(datetime(2026, 6, 15, 9, 30, 0), 10)
# 10 items · 3 per day · 4 días · día 4 solo tiene el 1er slot (9:30)
assert len(_t10) == 10 and _t10[9] == datetime(2026, 6, 18, 9, 30, 0)
try:
    space_timestamps(datetime(2026, 1, 1), 0)
    raise AssertionError("expected ValueError for n=0")
except ValueError:
    pass
