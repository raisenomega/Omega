"""Tests aria_learning_report._aggregate (DEBT-101) · agregación pura sin I/O.

Casos: semana sin actividad · solo nulls · evaluaciones mixtas · training pairs por cliente.
Mockear supabase no aporta valor → testeamos la lógica pura del agregador.
"""
from app.bc_cognition.application.aria_learning_report import _aggregate


def _m(cid: str, code: str, wc: bool | None) -> dict:
    return {"client_id": cid, "agent_code": code, "was_correct": wc}


def test_no_activity_returns_empty():
    """Sin memorias ni training_pairs → lista vacía (worker skip email)."""
    assert _aggregate([], [], {}) == []


def test_only_pending_decisions():
    """Solo was_correct=None → pending = total, correct=incorrect=0."""
    out = _aggregate([_m("c1", "aria_2", None), _m("c1", "aria_2", None)], [], {"c1": "Acme"})
    assert len(out) == 1
    c = out[0]
    assert c["client_id"] == "c1" and c["client_name"] == "Acme"
    assert c["decisions_total"] == 2 and c["pending"] == 2
    assert c["correct"] == 0 and c["incorrect"] == 0
    assert c["top_agents"] == ["aria_2"]
    assert c["training_pairs_generated"] == 0


def test_mixed_evaluations_and_top_agents():
    """True/False/None mezclados → counts correctos · top_agents ordenado por frecuencia."""
    mems = [
        _m("c1", "aria_2", True), _m("c1", "aria_2", True),
        _m("c1", "aria_3", False), _m("c1", "aria_4", None),
    ]
    out = _aggregate(mems, [], {"c1": "Acme"})
    c = out[0]
    assert c["decisions_total"] == 4
    assert c["correct"] == 2 and c["incorrect"] == 1 and c["pending"] == 1
    assert c["top_agents"][0] == "aria_2"  # 2 instances → primero
    assert set(c["top_agents"]) == {"aria_2", "aria_3", "aria_4"}


def test_training_pairs_counted_per_client():
    """training_pairs agrupados por client_id correctamente."""
    out = _aggregate(
        [_m("c1", "aria_2", True), _m("c2", "aria_2", True)],
        [{"client_id": "c1"}, {"client_id": "c1"}, {"client_id": "c2"}],
        {"c1": "A", "c2": "B"},
    )
    by_id = {c["client_id"]: c for c in out}
    assert by_id["c1"]["training_pairs_generated"] == 2
    assert by_id["c2"]["training_pairs_generated"] == 1


def test_null_client_id_skipped():
    """Memorias sin client_id (NOVA-owned · reseller-only) no rompen el agregado."""
    out = _aggregate([_m("c1", "aria_2", True), {"client_id": None, "agent_code": "x", "was_correct": True}], [], {"c1": "A"})
    assert len(out) == 1 and out[0]["decisions_total"] == 1
