"""DEBT-052 FASE 2 · tests del servicio de créditos prepagados."""
import asyncio
from unittest.mock import MagicMock, patch
import pytest


class _Resp:
    def __init__(self, data):
        self.data = data


class _Table:
    """Fake encadenable de supabase: select/eq/limit/update/insert → execute."""
    def __init__(self, store):
        self._store = store
        self._op = None

    def select(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def limit(self, *a, **k):
        return self

    def update(self, payload):
        self._op = ("update", payload)
        return self

    def insert(self, payload):
        self._op = ("insert", payload)
        return self

    def execute(self):
        if self._op and self._op[0] == "update":
            self._store["updated"] = self._op[1]
            return _Resp([self._op[1]])
        if self._op and self._op[0] == "insert":
            self._store.setdefault("ledger", []).append(self._op[1])
            return _Resp([self._op[1]])
        return _Resp(self._store.get("rows", []))


class _Client:
    def __init__(self, store):
        self._store = store

    def table(self, _name):
        return _Table(self._store)


def _patch(store):
    svc = MagicMock()
    svc.client = _Client(store)
    return patch("app.bc_billing.application.credits_service.get_supabase_service", return_value=svc)


def test_check_budget_no_row_passes():
    with _patch({"rows": []}):
        from app.bc_billing.application.credits_service import check_budget
        assert asyncio.run(check_budget("c1")) is True  # no enrolado → pasa


def test_check_budget_blocks_when_exhausted():
    with _patch({"rows": [{"budget_usd_mensual": 15, "consumido_usd": 15}]}):
        from app.bc_billing.application.credits_service import check_budget
        assert asyncio.run(check_budget("c1")) is False  # agotado → hard block


def test_check_budget_passes_with_balance():
    with _patch({"rows": [{"budget_usd_mensual": 15, "consumido_usd": 3}]}):
        from app.bc_billing.application.credits_service import check_budget
        assert asyncio.run(check_budget("c1")) is True


def test_debit_increments_and_ledgers():
    store = {"rows": [{"consumido_usd": 3.0}]}
    with _patch(store):
        from app.bc_billing.application.credits_service import debit
        asyncio.run(debit("c1", "RAFA", 0.05, "claude-sonnet-4-6"))
        assert store["updated"]["consumido_usd"] == pytest.approx(3.05)
        assert store["ledger"][0]["agent_code"] == "RAFA"


def test_needs_recharge_at_threshold():
    with _patch({"rows": [{"budget_usd_mensual": 100, "consumido_usd": 80}]}):
        from app.bc_billing.application.credits_service import needs_recharge
        assert asyncio.run(needs_recharge("c1")) is True  # 80% → saldo 20%


def test_check_budget_fail_open_on_db_error():
    """Error de infra (tabla ausente pre-db-push) → True · NUNCA bloquea generación."""
    svc = MagicMock()
    svc.client.table.side_effect = Exception("relation client_agent_credits does not exist")
    with patch("app.bc_billing.application.credits_service.get_supabase_service", return_value=svc):
        from app.bc_billing.application.credits_service import check_budget
        assert asyncio.run(check_budget("c1")) is True
