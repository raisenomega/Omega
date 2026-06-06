"""Punto 0 · Commit 2 · run_tool_loop devuelve content_ids del draft incluso si la narración
(2º generate) cae DESPUÉS de crearlo → el failure path de use_aria_message lo enlaza igual (el
contenido real existe). Split de test_aria_tools.py (C4) · reusa sus helpers."""
from app.bc_cognition.application.tests.test_aria_tools import _run, _resp, _tool_block
from app.bc_cognition.infrastructure._anthropic_types import ClaudeError


def test_draft_content_id_returned_even_if_narration_fails():
    block = _tool_block({"texto": "x"})
    text, err, content_ids = _run("client-A",
                     [(_resp(tool_calls=[block]), None), (None, ClaudeError("timeout", "narración cayó"))],
                     lambda client_id, payload: "new-cid")
    assert err is not None and text is None
    assert content_ids == ["new-cid"]   # el draft se creó · se enlaza igual
