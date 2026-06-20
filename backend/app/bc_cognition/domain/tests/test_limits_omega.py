"""Pin del límite de publicación de REX (ritual G2 · archivo sagrado limits_omega.py).

El límite es ANTI-SPAM y POR RED, no palanca de negocio: el freno real es el espaciado
de 2h (MIN_HORAS_ENTRE_POSTS → ~12/día físico). 24/red es un backstop generoso muy por
debajo del techo técnico de IG (100 posts/24h). Este test fija el valor para que un cambio
accidental se cace; cambiarlo a propósito exige rotar el SHA1 baseline.
"""
from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA


def test_max_posts_auto_per_dia_red_es_24() -> None:
    assert LIMITS_OMEGA["MAX_POSTS_AUTO_PER_DIA_RED"] == 24


def test_min_horas_entre_posts_sigue_siendo_2() -> None:
    # El anti-spam real (espaciado) no cambió: solo el backstop diario pasó a ser por red.
    assert LIMITS_OMEGA["MIN_HORAS_ENTRE_POSTS"] == 2
