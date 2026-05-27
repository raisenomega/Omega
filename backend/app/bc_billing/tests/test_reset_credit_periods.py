"""DEBT-052 FASE 4 · tests cron reset de periodos de credit packs."""
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

    def lte(self, *a, **k):
        return self

    def limit(self, *a, **k):
        return self

    def eq(self, *a, **k):
        return self

    def update(self, payload):
        self._op = payload
        return self

    def execute(self):
        if self._op is not None:
            self._store.setdefault("updates", []).append(self._op)
            return _Resp([self._op])
        return _Resp(self._store.get("due", []))


class _Client:
    def __init__(self, store):
        self._store = store

    def table(self, _n):
        return _Table(self._store)


def _patch(store):
    svc = MagicMock()
    svc.client = _Client(store)
    return patch("app.bc_billing.application.reset_credit_periods.get_supabase_service", return_value=svc)


def test_reset_clears_due_rows():
    store = {"due": [{"id": "a"}, {"id": "b"}]}
    with _patch(store):
        from app.bc_billing.application.reset_credit_periods import run_credit_period_reset
        r = asyncio.run(run_credit_period_reset())
        assert r["reset"] == 2 and r["failed"] == 0
        assert all(u["consumido_usd"] == 0 for u in store["updates"])


def test_reset_no_due_rows():
    with _patch({"due": []}):
        from app.bc_billing.application.reset_credit_periods import run_credit_period_reset
        r = asyncio.run(run_credit_period_reset())
        assert r["reset"] == 0 and r["failed"] == 0
