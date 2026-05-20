"""Canonical industry + region values · validación PATCH /clients/profile.

Cero imports externos (DDD A2). Sync manual con src/lib/client-constants.ts.
Decisión owner 2026-05-20: 8 industries PYME-core + 8 países LATAM
(target Hispano multi-país, no solo PR).
"""
from typing import Final

INDUSTRIES: Final[frozenset[str]] = frozenset({
    "retail",
    "restaurante",
    "servicios",
    "salud",
    "educacion",
    "tecnologia",
    "inmobiliaria",
    "otros",
})

REGIONS: Final[frozenset[str]] = frozenset({
    "PR",
    "USA",
    "DO",
    "MX",
    "CO",
    "AR",
    "ES",
    "otros",
})
