"""HERMES tab endpoint · latest-per-integration. G9 exime tests.
Fake supabase devuelve filas DESC; el handler debe quedarse con 1 por integración (la más reciente)."""
import asyncio
from unittest.mock import AsyncMock
from app.api.routes.security_dev.handlers import hermes_data as hd


class _FakeQuery:
    def __init__(self, rows): self._rows = rows
    def select(self, *a, **k): return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def execute(self): return type("R", (), {"data": self._rows})()


class _FakeClient:
    def __init__(self, rows): self._rows = rows
    def table(self, name): return _FakeQuery(self._rows)


def _patch(monkeypatch, rows):
    monkeypatch.setattr(hd, "require_super_owner", AsyncMock(return_value=None))
    monkeypatch.setattr(hd, "get_supabase_service", lambda: type("S", (), {"client": _FakeClient(rows)})())


def test_latest_por_integracion(monkeypatch):
    # 2 filas anthropic (la más reciente primero por DESC) + 1 brave → 2 integraciones, 1 c/u
    rows = [
        {"integration": "anthropic", "status": "ok", "last_use": "2026-06-01T11:00:00Z", "checked_at": "2026-06-01T11:00:00Z", "created_at": "2026-06-01T09:30:00Z"},
        {"integration": "anthropic", "status": "last_use_failed", "last_use": None, "checked_at": "2026-06-01T10:00:00Z", "created_at": "2026-06-01T08:00:00Z"},
        {"integration": "brave", "status": "ok", "last_use": "2026-06-01T10:55:00Z", "checked_at": "2026-06-01T10:55:00Z", "created_at": "2026-06-01T09:00:00Z"},
    ]
    _patch(monkeypatch, rows)
    out = asyncio.run(hd.handle_hermes_data("auth"))
    assert out["count"] == 2
    by = {i["integration"]: i for i in out["integrations"]}
    assert by["anthropic"]["status"] == "ok"   # la más reciente (11:00), no la failed (10:00)
    assert by["anthropic"]["created_at"] == "2026-06-01T09:30:00Z"  # "operativa desde" = created_at de la fila top
    assert by["brave"]["status"] == "ok"


def test_tabla_vacia(monkeypatch):
    _patch(monkeypatch, [])
    out = asyncio.run(hd.handle_hermes_data("auth"))
    assert out == {"integrations": [], "count": 0}


def test_supabase_caido_no_lanza(monkeypatch):
    monkeypatch.setattr(hd, "require_super_owner", AsyncMock(return_value=None))
    def _boom(): raise RuntimeError("supabase down")
    monkeypatch.setattr(hd, "get_supabase_service", lambda: _boom())
    out = asyncio.run(hd.handle_hermes_data("auth"))
    assert out["count"] == 0 and "error" in out  # best-effort
