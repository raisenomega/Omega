"""X2 · honestidad de la persona ARIA (P1): los niveles 3-4 NO deben anunciar capacidades
sin backend ni página a la que derivar (PDF/Markdown on-demand, predicciones a 30 días,
benchmarks de industria, reporte ejecutivo descargable). Falla contra la persona con las
promesas huérfanas; pasa tras el recorte quirúrgico. G9 exime tests."""
from app.bc_cognition.domain.persona_aria import LEVEL_CAPABILITIES

# Promesas huérfanas confirmadas (line-by-line 29 may): capacidad anunciada sin backend NI página.
# 5 promesas: reporte PDF/Markdown on-demand · predicciones 30 días · benchmarks de industria ·
# reporte ejecutivo descargable · predicción de mejores horarios (sin backend de scheduling/analytics).
_ORPHAN_PROMISES = (
    "pdf", "markdown", "30 días", "benchmarks anónimos de industria",
    "descargable", "predice mejores horarios",
)


def test_niveles_3_4_sin_promesas_huerfanas():
    blob = (LEVEL_CAPABILITIES[3] + " " + LEVEL_CAPABILITIES[4]).lower()
    leaked = [p for p in _ORPHAN_PROMISES if p in blob]
    assert not leaked, f"persona ARIA promete capacidades sin backend: {leaked}"

# La regla conductual anti-invención (no enumerar funciones de otra sección + firmeza) se MOVIÓ
# a application (_aria_tools._RESPONSE_RULES, anexada al final del system). Su test vive en
# test_aria_tools.py::test_response_rules_cierran_el_system_conversacional (fuente única · evita
# la doble fuente persona/app que divergiría · Q3). Aquí solo queda el guard del recorte (LEVEL_CAPABILITIES).
