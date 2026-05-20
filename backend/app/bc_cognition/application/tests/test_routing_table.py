"""Test X2 (audit FIX): routing_table cumple I2 para 4 codes ARIA.

Spec ARIA_NOVA_INTELLIGENCE §6: aria_1 = Haiku (conversacional básico)
· aria_2/3/4 = Sonnet (conversacional estándar/avanzado/near-NOVA).
"""
import pytest
from app.bc_cognition.domain.routing_table import resolve_model, get_tier

HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-6"


def test_aria_1_routes_to_haiku() -> None:
    assert resolve_model("aria_1") == HAIKU
    assert get_tier("aria_1") == "haiku"


@pytest.mark.parametrize("code", ["aria_2", "aria_3", "aria_4"])
def test_aria_2_3_4_route_to_sonnet(code: str) -> None:
    assert resolve_model(code) == SONNET
    assert get_tier(code) == "sonnet"


@pytest.mark.parametrize("code", ["aria_0", "aria_5", "aria_", "ARIA_1", "aria"])
def test_invalid_aria_codes_raise(code: str) -> None:
    with pytest.raises(KeyError):
        resolve_model(code)
