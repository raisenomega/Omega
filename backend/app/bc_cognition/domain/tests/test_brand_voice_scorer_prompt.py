"""CASO 2 (11 jun) · la escala del scorer queda ANCLADA (regression guard).

El scoring real lo hace Haiku (no unit-testeable offline · separación verificada
en vivo: on-brand 0.78 / neutro 0.62 / agresivo 0.15). Este test fija que la
ESCALA ANCLADA (4 bandas + regla 'matchea aprobados → 0.7+' + ejemplo bajo) siga
en el SYSTEM, para que no se borre en un refactor y el scorer no vuelva a
castigar contenido on-brand por matices menores."""
from app.bc_cognition.domain.brand_voice_scorer_prompt import (
    SYSTEM, MIN_SCORE, build_user_prompt,
)


def test_escala_anclada_presente():
    for band in ("0.9-1.0", "0.7-0.85", "0.5-0.65", "<0.5"):
        assert band in SYSTEM
    assert "DAÑA" in SYSTEM                       # <0.5 reservado para daño
    assert "aprobados" in SYSTEM                  # calibra contra ejemplos del cliente
    assert "matices menores" in SYSTEM            # no castigar on-brand por detalle


def test_umbral_sigue_en_0_7():
    assert MIN_SCORE == 0.7


def test_user_prompt_incluye_los_ejemplos_aprobados_reales():
    ref = {"corpus_count": 3, "top_keywords": [{"keyword": "calidad"}],
           "latest_approvals": ["ejemplo aprobado real del cliente"]}
    out = build_user_prompt("contenido a evaluar", ref)
    assert "ejemplo aprobado real del cliente" in out
    assert "contenido a evaluar" in out
