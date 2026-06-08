"""_media_guard.aspect_error / needs_ratio_check (pure · sin I/O). G9 exime tests.
Rango IG feed [0.8, 1.91] (autoridad: Instagram) · tiktok/fb lenientes."""
from app.api.routes.publishing._media_guard import aspect_error, needs_ratio_check


def test_ig_vertical_9x16_falla():
    err = aspect_error("instagram", 0.5625)  # 9:16
    assert err is not None and err.startswith("imagen_vertical_no_apta_feed_ig")


def test_ig_cuadrada_pasa():
    assert aspect_error("instagram", 1.0) is None


def test_ig_bordes_inclusivos_pasan():
    assert aspect_error("instagram", 0.8) is None   # 4:5 limite inferior
    assert aspect_error("instagram", 1.91) is None  # landscape limite superior


def test_ig_fuera_de_borde_falla():
    assert aspect_error("instagram", 0.79) is not None
    assert aspect_error("instagram", 1.92) is not None


def test_tiktok_vertical_leniente():
    assert aspect_error("tiktok", 0.5625) is None
    assert needs_ratio_check("tiktok") is False


def test_facebook_leniente():
    assert aspect_error("facebook", 0.5625) is None
    assert needs_ratio_check("facebook") is False


def test_needs_ratio_check_solo_instagram():
    assert needs_ratio_check("instagram") is True
