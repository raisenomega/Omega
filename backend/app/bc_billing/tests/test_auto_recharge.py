"""DEBT-052 FASE 4 (5/5) · tests auto-recarga (toggle + trigger honesto)."""
import asyncio
from unittest.mock import MagicMock, patch


class _Resp:
    def __init__(self, data): self.data = data


class _Q:
    def __init__(self, store, table):
        self.store, self.table, self._op = store, table, None

    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def update(self, p): self._op = ("update", p); return self
    def insert(self, p): self._op = ("insert", p); return self

    def execute(self):
        if self._op and self._op[0] == "update":
            self.store.setdefault("updates", {}).setdefault(self.table, []).append(self._op[1])
            return _Resp([self._op[1]])
        if self._op and self._op[0] == "insert":
            self.store.setdefault("inserts", {}).setdefault(self.table, []).append(self._op[1])
            return _Resp([self._op[1]])
        return _Resp(self.store.get("select", {}).get(self.table, []))


def _patch(store):
    svc = MagicMock()
    svc.client = MagicMock()
    svc.client.table = lambda name: _Q(store, name)
    return patch("app.bc_billing.application.auto_recharge_service.get_supabase_service", return_value=svc)


def _pack(auto):
    return {"tier": "starter", "deactivated_at": None, "auto_recharge": auto}


def test_set_toggle_on_active_pack():
    store = {"select": {"client_agent_credits": [{"packs": [_pack(False)]}]}}
    with _patch(store):
        from app.bc_billing.application.auto_recharge_service import set_auto_recharge
        r = asyncio.run(set_auto_recharge("c1", True))
        assert r["success"] is True
        assert store["updates"]["client_agent_credits"][0]["packs"][0]["auto_recharge"] is True


def test_set_toggle_not_enrolled():
    with _patch({"select": {"client_agent_credits": []}}):
        from app.bc_billing.application.auto_recharge_service import set_auto_recharge
        assert asyncio.run(set_auto_recharge("c1", True))["error_code"] == "not_enrolled"


def test_recharge_below_threshold_noop():
    store = {"select": {"client_agent_credits": [
        {"budget_usd_mensual": 25, "consumido_usd": 5, "packs": [_pack(True)]}]}}
    with _patch(store):
        from app.bc_billing.application.auto_recharge_service import maybe_auto_recharge
        assert asyncio.run(maybe_auto_recharge("c1"))["error_code"] == "below_threshold"
        assert "updates" not in store  # cero cambio de budget


def test_recharge_disabled_noop():
    store = {"select": {"client_agent_credits": [
        {"budget_usd_mensual": 25, "consumido_usd": 20, "packs": [_pack(False)]}]}}
    with _patch(store):
        from app.bc_billing.application.auto_recharge_service import maybe_auto_recharge
        assert asyncio.run(maybe_auto_recharge("c1"))["error_code"] == "disabled"
        assert "updates" not in store


def test_recharge_price_not_configured_honest_no_budget_change():
    store = {"select": {"client_agent_credits": [
        {"budget_usd_mensual": 25, "consumido_usd": 20, "packs": [_pack(True)]}]}}
    with _patch(store), patch(
        "app.bc_billing.application.auto_recharge_service.get_price_id_for_credit_pack", return_value=None
    ):
        from app.bc_billing.application.auto_recharge_service import maybe_auto_recharge
        r = asyncio.run(maybe_auto_recharge("c1"))
        assert r["error_code"] == "price_not_configured"
        assert "updates" not in store  # CERO fabricación de éxito


def test_recharge_happy_path_tops_up_budget():
    store = {"select": {
        "client_agent_credits": [{"budget_usd_mensual": 25, "consumido_usd": 20, "packs": [_pack(True)]}],
        "clients": [{"stripe_customer_id": "cus_1"}],
    }}
    adapter = MagicMock()
    with _patch(store), \
        patch("app.bc_billing.application.auto_recharge_service.get_price_id_for_credit_pack", return_value="price_x"), \
        patch("app.bc_billing.infrastructure.stripe_adapter.get_stripe_adapter", return_value=adapter):
        from app.bc_billing.application.auto_recharge_service import maybe_auto_recharge
        r = asyncio.run(maybe_auto_recharge("c1"))
        assert r["success"] is True and r["data"]["recharged_usd"] == 25.0
        assert store["updates"]["client_agent_credits"][0]["budget_usd_mensual"] == 50
        adapter.charge_off_session.assert_called_once_with("cus_1", "price_x")
        assert store["inserts"]["client_credit_ledger"][0]["agent_code"] == "__auto_recharge__"
