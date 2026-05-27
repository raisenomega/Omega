"""DEBT-052 FASE 4 · tests admin credit ops (transfer/release)."""
import asyncio
from unittest.mock import MagicMock, patch


class _Resp:
    def __init__(self, data): self.data = data


class _Table:
    """Fake encadenable supabase: rows por client_id · registra updates + ledger."""
    def __init__(self, store, name):
        self._store, self._name, self._op, self._eq = store, name, None, None

    def select(self, *a, **k): return self
    def limit(self, *a, **k): return self

    def eq(self, col, val):
        if col == "client_id": self._eq = val
        return self

    def insert(self, payload): self._op = ("insert", payload); return self
    def update(self, payload): self._op = ("update", payload); return self

    def execute(self):
        if self._name == "client_credit_ledger" and self._op and self._op[0] == "insert":
            self._store.setdefault("ledger", []).append(self._op[1]); return _Resp([self._op[1]])
        if self._op and self._op[0] == "update":
            self._store.setdefault("updates", {})[self._eq] = self._op[1]; return _Resp([self._op[1]])
        rows = self._store.get("rows", {})
        return _Resp([rows[self._eq]] if self._eq in rows else [])


def _patch(store):
    svc = MagicMock()
    svc.client = MagicMock()
    svc.client.table = lambda name: _Table(store, name)
    return patch("app.bc_billing.application.admin_credit_ops.get_supabase_service", return_value=svc)


def test_transfer_moves_budget():
    store = {"rows": {"A": {"budget_usd_mensual": 100, "consumido_usd": 20},
                      "B": {"budget_usd_mensual": 50, "consumido_usd": 0}}}
    with _patch(store):
        from app.bc_billing.application.admin_credit_ops import transfer_credits
        r = asyncio.run(transfer_credits("A", "B", 30))
        assert r["success"] is True
        assert store["updates"]["A"]["budget_usd_mensual"] == 70
        assert store["updates"]["B"]["budget_usd_mensual"] == 80
        assert len(store["ledger"]) == 2


def test_transfer_blocks_below_consumido():
    store = {"rows": {"A": {"budget_usd_mensual": 100, "consumido_usd": 90},
                      "B": {"budget_usd_mensual": 0, "consumido_usd": 0}}}
    with _patch(store):
        from app.bc_billing.application.admin_credit_ops import transfer_credits
        r = asyncio.run(transfer_credits("A", "B", 30))  # 100-30=70 < 90
        assert r["success"] is False and r["error_code"] == "insufficient_budget"


def test_transfer_not_enrolled():
    store = {"rows": {"A": {"budget_usd_mensual": 100, "consumido_usd": 0}}}
    with _patch(store):
        from app.bc_billing.application.admin_credit_ops import transfer_credits
        assert asyncio.run(transfer_credits("A", "B", 10))["error_code"] == "not_enrolled"


def test_transfer_same_client():
    from app.bc_billing.application.admin_credit_ops import transfer_credits
    assert asyncio.run(transfer_credits("A", "A", 10))["error_code"] == "same_client"


def test_release_reduces_consumido_floor_zero():
    store = {"rows": {"A": {"budget_usd_mensual": 100, "consumido_usd": 30}}}
    with _patch(store):
        from app.bc_billing.application.admin_credit_ops import release_credits
        r = asyncio.run(release_credits("A", 50))  # 30-50 → floor 0
        assert r["success"] is True and store["updates"]["A"]["consumido_usd"] == 0


def test_release_invalid_amount():
    from app.bc_billing.application.admin_credit_ops import release_credits
    assert asyncio.run(release_credits("A", 0))["error_code"] == "invalid_amount"
