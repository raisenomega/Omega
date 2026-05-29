"""Tests del borde impuro de conciencia temporal (resolve_tz / build_time_block).
Cubre el edge case del fix: tz NULL/inválida → fallback America/Puerto_Rico + warning (no bloquea)."""
from app.bc_cognition.application import _aria_temporal_context as tc


def test_tz_valida_se_respeta():
    _, name = tc.resolve_tz("America/New_York")
    assert name == "America/New_York"


def test_tz_null_cae_a_puerto_rico(caplog):
    with caplog.at_level("WARNING"):
        _, name = tc.resolve_tz(None)
    assert name == "America/Puerto_Rico"  # fallback owner-approved
    assert any("fallback" in r.message.lower() or "America/Puerto_Rico" in r.getMessage()
               for r in caplog.records)


def test_tz_invalida_cae_a_puerto_rico():
    _, name = tc.resolve_tz("Marte/Olympus_Mons")
    assert name == "America/Puerto_Rico"


def test_build_time_block_incluye_ahora_y_tz():
    block = tc.build_time_block("America/Puerto_Rico")
    assert "hoy es" in block.lower() and "America/Puerto_Rico" in block
