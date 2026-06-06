"""ESLABÓN 3 · DEBT-ARIA-NOVA-BRIDGE Commit 1 · fachada nova_aria_learning.
Conteos HONESTOS (nunca accuracy %), snippets truncados, fail-safe, _is_real_verdict excluye fallos API."""
from types import SimpleNamespace
from unittest.mock import patch

from app.bc_cognition.application import nova_aria_learning as facade


class _T:
    def __init__(self, data, raise_exc=False):
        self._data, self._raise = data, raise_exc
    def select(self, *a, **k): return self
    def in_(self, *a, **k): return self
    def execute(self):
        if self._raise:
            raise RuntimeError("supabase down")
        return SimpleNamespace(data=self._data)


class _Sb:
    def __init__(self, mems, clients, raise_exc=False):
        t = lambda n: _T(mems if n == "agent_memory" else clients, raise_exc)
        self.client = SimpleNamespace(table=t)


_ROWS = [
    {"context": "¿A qué se dedica mi negocio?", "decision": "Mantenimiento de zafacones.",
     "was_correct": None, "created_at": "t1"},
    {"context": "Dame ideas", "decision": "Antes/después de limpieza.", "was_correct": True, "created_at": "t2"},
    {"context": "Describe mi logo", "decision": "[failed:api_error]", "was_correct": False, "created_at": "t3"},
]


def test_for_client_real_snippets_and_honest_counts():
    with patch.object(facade, "fetch_recent_for_owner", return_value=_ROWS):
        out = facade.aria_learning_for_client(None, "afb9f578", limit=8)
    assert out["client_id"] == "afb9f578"
    assert out["interactions"][0]["context_snippet"] == "¿A qué se dedica mi negocio?"
    assert out["interactions"][0]["decision_snippet"].startswith("Mantenimiento")
    assert out["counts"] == {"total": 3, "with_real_verdict": 1, "no_signal": 2}  # #3 [failed] NO cuenta


def test_is_real_verdict_excludes_api_failures():
    assert facade._is_real_verdict({"decision": "[failed:api_error]", "was_correct": False}) is False
    assert facade._is_real_verdict({"decision": "ok", "was_correct": False}) is True
    assert facade._is_real_verdict({"decision": "ok", "was_correct": None}) is False


def test_snippet_truncated_to_150():
    big = [{"context": "x" * 400, "decision": "y", "was_correct": None, "created_at": "t"}]
    with patch.object(facade, "fetch_recent_for_owner", return_value=big):
        snip = facade.aria_learning_for_client(None, "c1")["interactions"][0]["context_snippet"]
    assert len(snip) <= 151 and snip.endswith("…")


def test_for_client_failsafe_and_no_client_id():
    with patch.object(facade, "fetch_recent_for_owner", side_effect=RuntimeError("boom")):
        assert facade.aria_learning_for_client(None, "c1")["counts"]["total"] == 0
    assert facade.aria_learning_for_client(None, None)["counts"]["total"] == 0


def test_global_groups_by_client_and_grand_total():
    mems = [
        {"client_id": "A", "agent_code": "aria", "was_correct": None, "decision": "ok"},
        {"client_id": "A", "agent_code": "aria", "was_correct": True, "decision": "ok"},
        {"client_id": "A", "agent_code": "aria", "was_correct": False, "decision": "[failed:x]"},
        {"client_id": "B", "agent_code": "aria", "was_correct": None, "decision": "ok"},
    ]
    out = facade.aria_learning_global(_Sb(mems, [{"id": "A", "name": "Zafacones"}, {"id": "B", "name": "Otro"}]))
    assert out["grand_total"] == 4
    biz = {b["client_id"]: b for b in out["businesses"]}
    assert biz["A"] == {"client_id": "A", "name": "Zafacones", "total": 3, "with_real_verdict": 1, "no_signal": 2}
    assert biz["B"]["with_real_verdict"] == 0
    assert out["businesses"][0]["client_id"] == "A"  # ordenado por total desc


def test_global_failsafe_and_empty():
    assert facade.aria_learning_global(_Sb([], [], raise_exc=True)) == {"businesses": [], "grand_total": 0}
    assert facade.aria_learning_global(_Sb([], []))["grand_total"] == 0


def test_no_accuracy_or_percentage_anywhere():
    with patch.object(facade, "fetch_recent_for_owner", return_value=_ROWS):
        c = facade.aria_learning_for_client(None, "c1")
    g = facade.aria_learning_global(_Sb([{"client_id": "A", "agent_code": "aria", "was_correct": True, "decision": "ok"}],
                                        [{"id": "A", "name": "Z"}]))
    blob = (str(c) + str(g)).lower()
    assert "accuracy" not in blob and "%" not in blob and "percent" not in blob
