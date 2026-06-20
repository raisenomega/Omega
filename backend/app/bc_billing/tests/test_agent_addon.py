"""DEBT-091 · tests agent add-on pricing + checkout + activation + dispatch."""
import asyncio
from unittest.mock import MagicMock, patch
from app.bc_billing.domain.agent_addon_pricing import (
    AGENT_ADDON_CODES, get_price_id_for_agent_addon,
)


def test_codes_are_the_five_tiers():
    assert AGENT_ADDON_CODES == {
        "publisher_esencial", "publisher_pro", "creative_esencial", "creative_pro", "trends_unico",
    }


def test_price_none_when_unconfigured():
    with patch("app.bc_billing.domain.agent_addon_pricing.settings") as s:
        s.stripe_price_agent_creative_pro = ""
        assert get_price_id_for_agent_addon("creative_pro") is None


def test_price_strips_when_configured():
    with patch("app.bc_billing.domain.agent_addon_pricing.settings") as s:
        s.stripe_price_agent_trends_unico = "  price_t  "
        assert get_price_id_for_agent_addon("trends_unico") == "price_t"


def test_checkout_rejects_invalid_code():
    from app.bc_billing.application.create_agent_addon_checkout import create_agent_addon_checkout
    r = asyncio.run(create_agent_addon_checkout("c1", "bogus", "s", "c"))
    assert r["success"] is False and r["error_code"] == "invalid_agent_addon_code"


def test_has_active_agent_addon():
    from app.bc_billing.application.create_agent_addon_checkout import has_active_agent_addon
    addons = [{"addon_code": "agent_creative_pro", "deactivated_at": None}]
    assert has_active_agent_addon(addons, "creative_pro") is True
    assert has_active_agent_addon(addons, "publisher_pro") is False


def test_activation_pushes_addon():
    from app.bc_billing.application._agent_addon_handlers import handle_agent_addon_activation
    captured = {}

    class _T:
        def select(self, *a, **k): return self
        def eq(self, *a, **k): return self
        def update(self, p):
            if "addons" in p: captured["addons"] = p["addons"]      # client_plans.addons
            if "rex_addon_active" in p: captured["rex"] = p["rex_addon_active"]  # flip clients (DEBT-098)
            return self
        def execute(self): return MagicMock(data=[{"addons": []}])

    sb = MagicMock()
    sb.client.table = lambda n: _T()
    asyncio.run(handle_agent_addon_activation("c1", "publisher_esencial", "sub_1", sb))
    assert captured["addons"][0]["addon_code"] == "agent_publisher_esencial"
    assert captured["rex"] is True  # publisher_* flipea rex_addon_active


def test_dispatch_routes_agent_addon():
    import app.bc_billing.application._checkout_dispatch as d
    called = {}

    async def fake(client_id, code, sub, sb):
        called["a"] = (client_id, code, sub)

    with patch.object(d, "handle_agent_addon_activation", fake):
        handled = asyncio.run(d.dispatch_addon_or_pack(
            {"client_id": "c1", "agent_addon_code": "creative_pro"}, "sub_9", MagicMock()))
    assert handled is True and called["a"] == ("c1", "creative_pro", "sub_9")
