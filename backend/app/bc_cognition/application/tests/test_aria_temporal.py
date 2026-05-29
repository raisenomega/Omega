"""Tests de conciencia temporal (domain puro) · deterministas: `now` inyectado, sin reloj real.
Cubre los 4 casos del fix: mañana 3pm → futuro · pasada → B2 · basura → B2 · None → B2."""
from datetime import datetime
from zoneinfo import ZoneInfo

from app.bc_cognition.domain.aria_temporal import format_now_block, resolve_future_iso

_PR = ZoneInfo("America/Puerto_Rico")
_NOW = datetime(2026, 5, 29, 11, 0, tzinfo=_PR)


def test_manana_3pm_es_futuro_valido():
    assert resolve_future_iso("2026-05-30T15:00", _NOW) == "2026-05-30T15:00"


def test_fecha_pasada_cae_a_b2():
    assert resolve_future_iso("2026-05-28T10:00", _NOW) is None


def test_iso_basura_cae_a_b2():
    assert resolve_future_iso("el martes", _NOW) is None


def test_none_cae_a_b2():
    assert resolve_future_iso(None, _NOW) is None


def test_iso_con_offset_futuro_se_conserva():
    assert resolve_future_iso("2026-05-30T15:00-04:00", _NOW) == "2026-05-30T15:00-04:00"


def test_format_now_block_es_determinista():
    block = format_now_block(_NOW, "America/Puerto_Rico")
    assert "hoy es" in block.lower()
    assert "29" in block and "2026" in block and "America/Puerto_Rico" in block
