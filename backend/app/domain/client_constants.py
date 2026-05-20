"""Canonical client onboarding constants · validación handlers clients_v3.

Cero imports externos (DDD A2). Sync manual con src/lib/onboarding-constants.ts.
Owner decisions:
  · 2026-05-20: 8 industries PYME-core + 8 países LATAM
  · 2026-05-20: wizard onboarding constants (BUSINESS_SIZES, TONES, etc.)
"""
from typing import Final

INDUSTRIES: Final[frozenset[str]] = frozenset({
    "retail", "restaurante", "servicios", "salud",
    "educacion", "tecnologia", "inmobiliaria", "otros",
})

REGIONS: Final[frozenset[str]] = frozenset({
    "PR", "USA", "DO", "MX", "CO", "AR", "ES", "otros",
})

BUSINESS_SIZES: Final[frozenset[str]] = frozenset({
    "solo", "pequeno", "mediano", "grande",
})

TONES: Final[frozenset[str]] = frozenset({
    "profesional", "casual", "divertido",
    "tecnico", "inspirador", "autoritario",
})

EMOJI_USAGE: Final[frozenset[str]] = frozenset({
    "never", "rarely", "balanced", "frequent",
})

HASHTAG_STRATEGY: Final[frozenset[str]] = frozenset({
    "minimal", "balanced", "many",
})

PRIMARY_GOALS: Final[frozenset[str]] = frozenset({
    "awareness", "leads", "sales", "community", "retention",
})

AUDIENCE_AGE_RANGES: Final[frozenset[str]] = frozenset({
    "13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+",
})

GENDERS: Final[frozenset[str]] = frozenset({
    "male", "female", "mixed", "non_binary", "any",
})

CONTENT_FORMATS: Final[frozenset[str]] = frozenset({
    "carousel", "reels", "photos", "long_video", "stories",
})

PUBLISHING_FREQUENCIES: Final[frozenset[str]] = frozenset({
    "daily", "few_per_week", "weekly", "biweekly", "monthly", "irregular",
})
