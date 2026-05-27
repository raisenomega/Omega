"""DEBT-052 FASE 4 · tests enrolamiento credit pack + dispatch webhook."""
import asyncio
from unittest.mock import MagicMock, patch


class _Resp:
    def __init__(self, data):
        self.data = data


class _Table:
    def __init__(self, store):
        self._store = store
        self._op = None

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def insert(self, payload):
        self._op = ("insert", payload)
        return self

    def update(self, payload):
        self._op = ("update", payload)
        return self

    def execute(self):
        if self._op and self._op[0] == "insert":
            self._store["inserted"] = self._op[1]
            return _Resp([self._op[1]])
        if self._op and self._op[0] == "update":
            self._store["updated"] = self._op[1]
            return _Resp([self._op[1]])
        return _Resp(self._store.get("rows", []))


class _Client:
    def __init__(self, store):
        self._store = store

    def table(self, _n):
        return _Table(self._store)


def _svc(store):
    s = MagicMock()
    s.client = _Client(store)
    return s


def test_enrollment_inserts_when_no_row():
    from app.bc_billing.application._credit_pack_handlers import handle_credit_pack_enrollment
    store = {"rows": []}
    asyncio.run(handle_credit_pack_enrollment("c1", "starter", "sub_1", _svc(store)))
    ins = store["inserted"]
    assert ins["budget_usd_mensual"] == 25.0
    assert ins["consumido_usd"] == 0
    assert ins["packs"][0]["tier"] == "starter"
    assert ins["packs"][0]["stripe_subscription_id"] == "sub_1"
    assert ins["packs"][0]["auto_recharge"] is False


def test_enrollment_updates_when_row_exists():
    from app.bc_billing.application._credit_pack_handlers import handle_credit_pack_enrollment
    store = {"rows": [{"id": "x"}]}
    asyncio.run(handle_credit_pack_enrollment("c1", "ultra", "sub_2", _svc(store)))
    assert store["updated"]["budget_usd_mensual"] == 119.0


def test_enrollment_unknown_tier_noops():
    from app.bc_billing.application._credit_pack_handlers import handle_credit_pack_enrollment
    store = {"rows": []}
    asyncio.run(handle_credit_pack_enrollment("c1", "bogus", "sub_3", _svc(store)))
    assert "inserted" not in store and "updated" not in store


def test_dispatch_routes_credit_pack():
    import app.bc_billing.application._checkout_dispatch as d
    called = {}

    async def fake_enroll(client_id, code, sub, sb):
        called["args"] = (client_id, code, sub)

    with patch.object(d, "handle_credit_pack_enrollment", fake_enroll):
        handled = asyncio.run(d.dispatch_addon_or_pack(
            {"client_id": "c1", "credit_pack_code": "plus"}, "sub_9", MagicMock()))
    assert handled is True and called["args"] == ("c1", "plus", "sub_9")


def test_dispatch_returns_false_for_plan_upgrade():
    import app.bc_billing.application._checkout_dispatch as d
    handled = asyncio.run(d.dispatch_addon_or_pack(
        {"client_id": "c1", "target_plan": "pro"}, "sub_1", MagicMock()))
    assert handled is False
