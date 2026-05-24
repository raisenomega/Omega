"""Industry defaults · Brand DNA fallback · DEBT-CL-019.

Capa pura · cero imports externos (A2). Tone + keywords típicos por
vertical para cuando el cliente NO tiene corpus aún (cliente nuevo) y
el handler genera contenido. Cero data inventada · estos defaults
guían el estilo inicial · brand_voice_corpus real toma over cuando el
cliente aprueba posts (trigger SQL invalida cache automáticamente).

Verticales cubiertos: los 8 del mapping _INDUSTRY_TO_VERTICAL en
api/routes/content_lab_v3/handlers/generate_text.py.

Self-checks al import (patrón limits_omega · video_entitlements ·
timestamp_spacer).
"""
from types import MappingProxyType
from typing import Final, Optional

_DEFAULTS_RAW = {
    "restaurant":   {"tone": ["warm", "auténtico", "apetitoso"],
                     "keywords": ["sabor", "ingredientes", "casa", "fresco", "plato"]},
    "real_estate":  {"tone": ["profesional", "aspiracional", "confiable"],
                     "keywords": ["hogar", "propiedad", "oportunidad", "ubicación", "inversión"]},
    "health":       {"tone": ["empático", "profesional", "educativo"],
                     "keywords": ["bienestar", "prevención", "salud", "paciente", "tratamiento"]},
    "construction": {"tone": ["técnico", "orgulloso", "confiable"],
                     "keywords": ["proyecto", "calidad", "equipo", "obra", "transformación"]},
    "technology":   {"tone": ["innovador", "claro", "profesional"],
                     "keywords": ["solución", "innovación", "tecnología", "eficiencia", "futuro"]},
    "retail":       {"tone": ["cercano", "persuasivo", "energético"],
                     "keywords": ["oferta", "producto", "calidad", "novedad", "descubrí"]},
    "education":    {"tone": ["motivador", "claro", "profesional"],
                     "keywords": ["aprender", "conocimiento", "crecimiento", "futuro", "oportunidad"]},
    "services":     {"tone": ["confiable", "profesional", "cercano"],
                     "keywords": ["servicio", "solución", "experiencia", "atención", "calidad"]},
}

INDUSTRY_DEFAULTS: Final[MappingProxyType] = MappingProxyType({
    k: MappingProxyType(v) for k, v in _DEFAULTS_RAW.items()
})


def get_defaults(vertical: Optional[str]) -> Optional[MappingProxyType]:
    """Retorna defaults frozen para el vertical · None si no mapeado."""
    if not vertical:
        return None
    return INDUSTRY_DEFAULTS.get(vertical)


# Self-checks al import (fail-fast · sin pytest infra)
assert "restaurant" in INDUSTRY_DEFAULTS
assert len(INDUSTRY_DEFAULTS) == 8
assert get_defaults("unknown") is None
assert get_defaults(None) is None
assert get_defaults("") is None
assert get_defaults("restaurant")["tone"][0] == "warm"
try:
    INDUSTRY_DEFAULTS["test"] = None  # type: ignore[index]
    raise AssertionError("INDUSTRY_DEFAULTS mutable")
except TypeError:
    pass
