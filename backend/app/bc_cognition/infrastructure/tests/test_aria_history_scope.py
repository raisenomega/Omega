"""Switcher V1 · aislamiento de historial/borrado ARIA por negocio (DEBT-ARIA-CHAT-CLIENT-ID
+ DEBT-ARIA-DELETE-HISTORY-LIMIT1). Fake Supabase registra los .eq() aplicados al query.
G9 exime tests."""
from app.bc_cognition.infrastructure import aria_repository as repo
from app.bc_cognition.infrastructure import aria_memory_repository as mem


class _FakeQuery:
    def __init__(self, rows, eqs):
        self._rows, self._eqs = rows, eqs

    def select(self, *a, **k): return self
    def eq(self, col, val): self._eqs.append((col, val)); return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def delete(self): return self
    def execute(self): return type("R", (), {"data": self._rows, "count": len(self._rows)})()


class _FakeClient:
    def __init__(self, rows, eqs):
        self._rows, self._eqs = rows, eqs

    def table(self, name): return _FakeQuery(self._rows, self._eqs)


class _FakeSupabase:
    def __init__(self, rows=None):
        self._eqs = []
        self.client = _FakeClient(rows or [], self._eqs)


def test_history_endpoint_scoped_by_client():
    sb = _FakeSupabase([{"role": "user", "content": "x", "aria_level": 2, "created_at": "t"}])
    repo.load_history_for_endpoint(sb, "user-1", client_id="biz-A")
    assert ("user_id", "user-1") in sb._eqs
    assert ("client_id", "biz-A") in sb._eqs


def test_history_endpoint_without_client_is_legacy():
    sb = _FakeSupabase([])
    repo.load_history_for_endpoint(sb, "user-1")
    assert ("user_id", "user-1") in sb._eqs
    assert not any(c == "client_id" for c, _ in sb._eqs)


def test_recent_history_scoped_by_client():
    sb = _FakeSupabase([])
    repo.load_recent_history(sb, "user-1", window=5, client_id="biz-A")
    assert ("client_id", "biz-A") in sb._eqs


def test_recent_history_without_client_is_legacy():
    sb = _FakeSupabase([])
    repo.load_recent_history(sb, "user-1", window=5)
    assert not any(c == "client_id" for c, _ in sb._eqs)


def test_delete_history_scoped_by_client():
    sb = _FakeSupabase([])
    mem.delete_aria_history(sb, "user-1", client_id="biz-A")
    assert ("user_id", "user-1") in sb._eqs
    assert ("client_id", "biz-A") in sb._eqs


def test_delete_history_without_client_is_legacy():
    sb = _FakeSupabase([])
    mem.delete_aria_history(sb, "user-1")
    assert ("user_id", "user-1") in sb._eqs
    assert not any(c == "client_id" for c, _ in sb._eqs)
