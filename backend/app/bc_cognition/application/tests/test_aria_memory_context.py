"""Tests for _aria_memory_context · pure formatter + best-effort orchestration.

Located in application/tests/ (no domain/tests/ aún · mismo patrón que
test_brand_dna_builder.py de T3). Mockea fetch_recent_for_owner vía
monkeypatch porque depende de Supabase.
"""
from datetime import datetime, timezone, timedelta

from app.bc_cognition.application import _aria_memory_context as ctx


_NOW = datetime.now(timezone.utc)
_TARGET = "app.bc_cognition.application._aria_memory_context.fetch_recent_for_owner"
_SIMILAR = "app.bc_cognition.application._aria_memory_context.fetch_similar_for_owner"


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


# ── DEBT-048 attention-based retrieval ──────────────────────────────────────

def test_query_uses_semantic_when_available(monkeypatch) -> None:
    """Con query + similar no-vacío → usa la memoria semántica, no la cronológica."""
    similar = [_row(1, True, "presupuesto ads", "empezá con $5/día en IG")]
    monkeypatch.setattr(_SIMILAR, lambda *a, **k: similar)
    monkeypatch.setattr(_TARGET, lambda *a, **k: [_row(99, None, "otra cosa", "otra resp")])
    out = ctx.load_and_format_memory(None, client_id="c1", reseller_id=None, query="cuánto invierto en ads")
    assert "presupuesto ads" in out
    assert "otra cosa" not in out


def test_query_falls_back_to_chronological_when_semantic_empty(monkeypatch) -> None:
    """Voyage down / RPC vacío (similar=[]) → fallback seamless a cronológico."""
    monkeypatch.setattr(_SIMILAR, lambda *a, **k: [])
    monkeypatch.setattr(_TARGET, lambda *a, **k: [_row(1, True, "cronológico", "fallback resp")])
    out = ctx.load_and_format_memory(None, client_id="c1", reseller_id=None, query="algo")
    assert "cronológico" in out


def test_no_query_skips_semantic_path(monkeypatch) -> None:
    """Sin query → ni siquiera toca fetch_similar_for_owner (path cronológico puro)."""
    def _should_not_run(*a, **k):
        raise AssertionError("fetch_similar_for_owner no debe llamarse sin query")
    monkeypatch.setattr(_SIMILAR, _should_not_run)
    monkeypatch.setattr(_TARGET, lambda *a, **k: [_row(1, True, "solo cronológico", "resp")])
    out = ctx.load_and_format_memory(None, client_id="c1", reseller_id=None)
    assert "solo cronológico" in out
