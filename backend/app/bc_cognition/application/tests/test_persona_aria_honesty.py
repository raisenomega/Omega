"""X2 · honestidad de la persona ARIA (P1): los niveles 3-4 NO deben anunciar capacidades
sin backend ni página a la que derivar (PDF/Markdown on-demand, predicciones a 30 días,
benchmarks de industria, reporte ejecutivo descargable). Falla contra la persona con las
promesas huérfanas; pasa tras el recorte quirúrgico. G9 exime tests."""
from app.bc_cognition.domain.persona_aria import LEVEL_CAPABILITIES, build_system_prompt

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


def test_persona_constraint_anti_invencion_balanceado():
    """La persona debe (a) prohibir inventar/enumerar funciones de OTRAS secciones al dirigir,
    y (b) reafirmar firmeza sobre lo que ARIA SÍ hace (no caer en el P1 opuesto: negar lo propio).
    Falla contra la persona actual (sin la regla); pasa tras añadir el constraint balanceado."""
    p = build_system_prompt(3, "client").lower()
    # (a) prohibición de inventar/enumerar capacidades ajenas
    assert "no inventes ni enumeres" in p, "falta la prohibición de inventar funciones de otra sección"
    assert "sin prometer" in p, "falta el patrón 'dirigir sin prometer'"
    # (b) firmeza sobre lo propio (anti P1 opuesto · que no se vuelva medrosa)
    assert "nunca lo dudes ni lo niegues" in p, "falta reafirmar lo que ARIA SÍ hace (anti P1 opuesto)"
