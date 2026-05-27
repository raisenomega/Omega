"""DEBT-052 FASE 4 · tests credit_pack_pricing + checkout validation."""
import asyncio
from unittest.mock import patch
from app.bc_billing.domain.credit_pack_pricing import (
    CREDIT_PACK_CODES, get_price_id_for_credit_pack,
)


def test_credit_pack_codes_are_the_four_tiers():
    assert CREDIT_PACK_CODES == {"micro", "starter", "plus", "ultra"}


def test_price_id_none_when_unconfigured():
    with patch("app.bc_billing.domain.credit_pack_pricing.settings") as s:
        s.stripe_price_credit_pack_micro = ""
        assert get_price_id_for_credit_pack("micro") is None


def test_price_id_strips_and_returns_when_configured():
    with patch("app.bc_billing.domain.credit_pack_pricing.settings") as s:
        s.stripe_price_credit_pack_starter = "  price_abc  "
        assert get_price_id_for_credit_pack("starter") == "price_abc"


def test_unknown_tier_returns_none():
    assert get_price_id_for_credit_pack("nonexistent") is None


def test_checkout_rejects_invalid_code():
    """Validación pre-I/O · no toca Stripe ni Supabase."""
    from app.bc_billing.application.create_credit_pack_checkout import create_credit_pack_checkout
    r = asyncio.run(create_credit_pack_checkout("c1", "bogus", "s", "c"))
    assert r["success"] is False and r["error_code"] == "invalid_credit_pack_code"
