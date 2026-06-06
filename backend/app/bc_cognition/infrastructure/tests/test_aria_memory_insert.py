"""Punto 0 · Commit 1 · insert_agent_memory guarda content_id en aria_nba_id (enlace al contenido).
forward-only: None cuando la interacción no generó contenido (Q&A) → no-signal honesto."""
from types import SimpleNamespace
from unittest.mock import patch

from app.bc_cognition.infrastructure import aria_memory_repository as repo


def _capture():
    cap = {}

    def insert(payload):
        cap["payload"] = payload
        return SimpleNamespace(execute=lambda: SimpleNamespace(data=[{"id": "x"}]))

    sb = SimpleNamespace(client=SimpleNamespace(table=lambda name: SimpleNamespace(insert=insert)))
    return sb, cap


def test_aria_nba_id_set_when_content_id_passed():
    sb, cap = _capture()
    with patch.object(repo, "_embed_memory", return_value=None):
        repo.insert_agent_memory(sb, "u", "c", None, "msg", "resp", 1, "evt-behavioral",
                                 content_id="content-123")
    assert cap["payload"]["aria_nba_id"] == "content-123"
    assert cap["payload"]["source_event_id"] == "evt-behavioral"  # el behavioral sigue intacto
    assert cap["payload"]["agent_code"] == "aria"


def test_aria_nba_id_null_when_no_content():
    sb, cap = _capture()
    with patch.object(repo, "_embed_memory", return_value=None):
        repo.insert_agent_memory(sb, "u", "c", None, "msg", "resp", 1, "evt")
    assert cap["payload"]["aria_nba_id"] is None
