"""HERMES fase 1.5 · usage-tracking (insert-on-change + update last_use). G9 exime tests.
Testea el núcleo síncrono _apply_usage con un fake supabase que cuenta inserts vs updates."""
import asyncio
from app.bc_cognition.infrastructure import hermes_usage as hu


class _FakeQuery:
    def __init__(self, store, last_status):
        self._store, self._last = store, last_status
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def insert(self, row): self._store["inserts"].append(row); return self
    def update(self, row): self._store["updates"].append(row); return self
    def execute(self):
        # select → devuelve la última fila conocida (o vacío); insert/update → data irrelevante
        data = [{"id": "x1", "status": self._last}] if self._last is not None else []
        return type("R", (), {"data": data})()


class _FakeClient:
    def __init__(self, last_status):
        self.store = {"inserts": [], "updates": []}
        self._last = last_status
    def table(self, name): return _FakeQuery(self.store, self._last)


def test_mismo_estado_hace_update_no_insert():
    """ok→ok (estado ya 'ok') → UPDATE last_use · NO inserta (no multiplica filas)."""
    sb = _FakeClient(last_status="ok")
    res = hu._apply_usage(sb, "anthropic", ok=True, detail=None)
    assert res == "update"
    assert len(sb.store["updates"]) == 1 and len(sb.store["inserts"]) == 0
    assert "last_use" in sb.store["updates"][0]


def test_cambio_de_estado_inserta_fila_nueva():
    """ok→failed (estado era 'ok') → INSERT fila nueva con last_use_failed (transición = incidente)."""
    sb = _FakeClient(last_status="ok")
    res = hu._apply_usage(sb, "anthropic", ok=False, detail="api_error 500")
    assert res == "insert"
    assert len(sb.store["inserts"]) == 1 and len(sb.store["updates"]) == 0
    row = sb.store["inserts"][0]
    assert row["status"] == "last_use_failed" and row["detail"] == "api_error 500"


def test_primera_vez_sin_historial_inserta():
    """sin fila previa → INSERT (no hay qué actualizar)."""
    sb = _FakeClient(last_status=None)
    res = hu._apply_usage(sb, "brave", ok=True, detail=None)
    assert res == "insert" and sb.store["inserts"][0]["status"] == "ok"


def test_recovery_failed_a_ok_inserta():
    """failed→ok (recuperación) → INSERT (transición · queda en el historial)."""
    sb = _FakeClient(last_status="last_use_failed")
    res = hu._apply_usage(sb, "stripe", ok=True, detail=None)
    assert res == "insert" and sb.store["inserts"][0]["status"] == "ok"


def test_record_mcp_use_sin_loop_no_lanza():
    """record_mcp_use en contexto sync (sin event loop) → no lanza (best-effort)."""
    hu.record_mcp_use("anthropic", ok=True)  # no debe explotar


def test_record_async_supabase_caido_no_lanza(monkeypatch):
    """Si Supabase falla, _record_async traga el error (observabilidad, no camino crítico)."""
    def _boom(): raise RuntimeError("supabase down")
    monkeypatch.setattr(hu, "get_supabase_service", lambda: _boom())
    asyncio.run(hu._record_async("anthropic", ok=True, detail=None))  # no lanza
