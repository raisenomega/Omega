"""Punto 0 · Commit 3 · _decide cierra was_correct usando aria_nba_id (id del contenido enlazado),
no source_event_id (behavioral). 4 ramas: approved⇒True · rejected⇒False · null+>72h⇒"Sin señal" · null+<72h⇒None.
+ draft (no veredicto) cae a "Sin señal", no inventa."""
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

from app.bc_cognition.application.evaluate_decisions import _decide

_NOW = datetime(2026, 6, 6, 12, 0, tzinfo=timezone.utc)


def _sb(status):
    """sb cuyo content_lab_generated.select().eq().limit().execute().data = [{status}] (o [] si None)."""
    data = [{"status": status}] if status is not None else []
    chain = SimpleNamespace()
    chain.select = lambda *a, **k: chain
    chain.eq = lambda *a, **k: chain
    chain.limit = lambda *a, **k: chain
    chain.execute = lambda: SimpleNamespace(data=data)
    return SimpleNamespace(table=lambda name: chain)


def _row(aria_nba_id, age_hours):
    created = (_NOW - timedelta(hours=age_hours)).isoformat()
    # source_event_id SIGUE en la fila (behavioral) · ya no es la key del veredicto
    return {"id": "r1", "source_event_id": "behav-1", "aria_nba_id": aria_nba_id, "created_at": created}


def test_approved_content_sets_true():
    v = _decide(_sb("approved"), _row("content-1", 100), _NOW)
    assert v["was_correct"] is True and "acepto" in v["outcome"]


def test_rejected_content_sets_false():
    v = _decide(_sb("rejected"), _row("content-1", 100), _NOW)
    assert v["was_correct"] is False and "rechazo" in v["outcome"]


def test_null_link_over_72h_no_signal():
    v = _decide(_sb(None), _row(None, 100), _NOW)
    assert v["was_correct"] is None and v["outcome"] == "Sin señal 72h"


def test_null_link_under_72h_returns_none():
    assert _decide(_sb(None), _row(None, 10), _NOW) is None


def test_draft_status_is_not_a_verdict_falls_to_no_signal():
    # contenido en draft (ni pos ni neg) + >72h → sin señal · NO inventa veredicto
    v = _decide(_sb("draft"), _row("content-1", 100), _NOW)
    assert v["was_correct"] is None and v["outcome"] == "Sin señal 72h"
