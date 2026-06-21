"""HERMES detail · derivación de incidentes (PURA) + empty honesto del handler. G9 exime tests.
rows_desc = created_at DESC (como los devuelve mcp_health_log). Cada last_use_failed = ventana de fallo."""
import asyncio
from unittest.mock import AsyncMock
from app.api.routes.security_dev.handlers import hermes_detail as hd


def _row(status, created_at, last_use=None, detail=None):
    return {"status": status, "detail": detail, "last_use": last_use,
            "checked_at": created_at, "created_at": created_at}


def test_incidente_cerrado_ok_fail_ok():
    # ok → fail → ok = 1 incidente CERRADO (started=inicio del fail, recovered=el ok siguiente).
    rows = [  # DESC: nuevo → viejo
        _row("ok", "2026-06-01T12:00:00Z", last_use="2026-06-01T12:00:00Z"),
        _row("last_use_failed", "2026-06-01T11:00:00Z", last_use="2026-06-01T11:05:00Z", detail="zernio_503:upstream"),
        _row("ok", "2026-06-01T10:00:00Z", last_use="2026-06-01T10:00:00Z"),
    ]
    inc = hd.derive_incidents(rows)
    assert len(inc) == 1
    assert inc[0]["started_at"] == "2026-06-01T11:00:00Z"
    assert inc[0]["recovered_at"] == "2026-06-01T12:00:00Z"
    assert inc[0]["last_failure_at"] == "2026-06-01T11:05:00Z"
    assert inc[0]["detail"] == "zernio_503:upstream"


def test_incidente_abierto_ultima_fila_fail():
    # última fila (más nueva) = fail → incidente ABIERTO (sin recuperación aún).
    rows = [
        _row("last_use_failed", "2026-06-01T11:00:00Z", last_use="2026-06-01T11:00:00Z", detail="zernio_500"),
        _row("ok", "2026-06-01T10:00:00Z", last_use="2026-06-01T10:00:00Z"),
    ]
    inc = hd.derive_incidents(rows)
    assert len(inc) == 1 and inc[0]["recovered_at"] is None
    assert inc[0]["started_at"] == "2026-06-01T11:00:00Z"


def test_sin_incidentes_solo_ok():
    # todo ok → 0 incidentes (verdad honesta: "todo en orden").
    rows = [
        _row("ok", "2026-06-01T12:00:00Z", last_use="2026-06-01T12:00:00Z"),
        _row("ok", "2026-06-01T10:00:00Z", last_use="2026-06-01T10:00:00Z"),
    ]
    assert hd.derive_incidents(rows) == []


class _FakeQuery:
    def __init__(self, rows): self._rows = rows
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def execute(self): return type("R", (), {"data": self._rows})()


def test_handler_sin_filas_devuelve_vacio_honesto(monkeypatch):
    # Integración sin historial → timeline [] + incidents [] · CERO datos inventados (verdad honesta).
    monkeypatch.setattr(hd, "require_super_owner", AsyncMock(return_value=None))
    monkeypatch.setattr(hd, "get_supabase_service",
                        lambda: type("S", (), {"client": type("C", (), {"table": lambda s, n: _FakeQuery([])})()})())
    out = asyncio.run(hd.handle_hermes_detail("zernio", "auth"))
    assert out == {"integration": "zernio", "timeline": [], "incidents": []}
