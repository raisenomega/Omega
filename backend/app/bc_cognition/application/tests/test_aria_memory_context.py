"""Tests for _aria_memory_context · pure formatter + best-effort orchestration.

Located in application/tests/ (no domain/tests/ aún · mismo patrón que
test_brand_dna_builder.py de T3). Mockea fetch_recent_for_owner vía
monkeypatch porque depende de Supabase.
"""
from datetime import datetime, timezone, timedelta

from app.bc_cognition.application import _aria_memory_context as ctx


_NOW = datetime.now(timezone.utc)
_TARGET = "app.bc_cognition.application._aria_memory_context.fetch_recent_for_owner"


def _row(hours_ago=1, was_correct=True,
         context="qué hago en IG hoy", decision="publicá martes 7pm con un Reel corto") -> dict:
    return {
        "id": "r1", "context": context, "decision": decision,
        "was_correct": was_correct,
        "created_at": (_NOW - timedelta(hours=hours_ago)).isoformat(),
        "agent_code": "aria",
    }


def test_no_owner_returns_empty() -> None:
    assert ctx.load_and_format_memory(None, None, None) == ""


def test_empty_rows_returns_empty(monkeypatch) -> None:
    monkeypatch.setattr(_TARGET, lambda *a, **k: [])
    assert ctx.load_and_format_memory(None, client_id="c1", reseller_id=None) == ""


def test_three_rows_emits_header_and_bullets(monkeypatch) -> None:
    rows = [
        _row(1, True, "qué hago en IG", "publicá martes 7pm"),
        _row(25, False, "subir precios", "no, eso aleja clientes"),
        _row(50, None, "reels o stories", "reels generan más engagement"),
    ]
    monkeypatch.setattr(_TARGET, lambda *a, **k: rows)
    out = ctx.load_and_format_memory(None, client_id="c1", reseller_id=None)
    assert "# MEMORIA RECIENTE" in out
    assert "✓" in out and "✗" in out and "?" in out
    assert out.count("\n- [") == 3


def test_token_budget_truncates_rows(monkeypatch) -> None:
    long_text = "palabra " * 200
    rows = [_row(1, True, long_text, long_text) for _ in range(10)]
    monkeypatch.setattr(_TARGET, lambda *a, **k: rows)
    out = ctx.load_and_format_memory(
        None, client_id="c1", reseller_id=None, max_tokens=100,
    )
    assert len(out) <= 100 * 4 + len(ctx._HEADER) + 10
    assert "# MEMORIA RECIENTE" in out


def test_fetch_exception_returns_empty(monkeypatch) -> None:
    def _boom(*a, **k):
        raise RuntimeError("supabase down")
    monkeypatch.setattr(_TARGET, _boom)
    assert ctx.load_and_format_memory(None, client_id="c1", reseller_id=None) == ""
