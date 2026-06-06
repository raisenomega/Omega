"""Punto 0 · Commit 2 · use_aria_message threadea content_id al agent_memory (ambos paths).
Desempaque de la tupla de 3 de run_tool_loop + content_id=content_ids[0] if content_ids else None.
Mock de TODA la I/O (cero API/DB) · captura el kwargs de los safe_insert de agent_memory."""
import asyncio
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, MagicMock

from app.bc_cognition.application import use_aria_message as uam
from app.bc_cognition.infrastructure._anthropic_types import ClaudeError


def _run_uam(tool_loop_return):
    calls = []

    async def _safe_insert(label, fn, *a, **k):
        calls.append((label, k))
        return "evt-id"  # el 1er safe_insert (behavioral_sent) da el event_id

    repo_mock = MagicMock()
    repo_mock.safe_insert = _safe_insert
    repo_mock.fetch_aria_context = MagicMock(return_value=None)   # ctx None → bloques cliente vacíos
    repo_mock.load_recent_history = MagicMock(return_value=[])

    patches = {
        "get_supabase_service": MagicMock(return_value=MagicMock()),
        "sanitize_input": MagicMock(return_value=(SimpleNamespace(action="safe", clean_text="msg", flags=[]), None)),
        "build_system_prompt": MagicMock(return_value="base"),
        "fetch_web_context": AsyncMock(return_value=""),
        "load_and_format_memory": MagicMock(return_value=""),
        "build_time_block": MagicMock(return_value=""),
        "build_client_context_block": MagicMock(return_value=""),
        "build_user_content": AsyncMock(return_value="x"),
        "run_tool_loop": AsyncMock(return_value=tool_loop_return),
        "get_agent_code_for_level": MagicMock(return_value="aria_1"),
        "get_history_window": MagicMock(return_value=5),
    }
    with patch.object(uam, "repo", repo_mock), patch.multiple(uam, **patches):
        asyncio.run(uam.use_aria_message("user-1", "hola", client_id="client-A", level=1))
    return calls


def _content_id(calls, label):
    rows = [k for (lbl, k) in calls if lbl == label]
    return rows[0].get("content_id") if rows else "NO_CALL"


def test_happy_path_links_content_id():
    calls = _run_uam(("reply", None, ["cid-X"]))
    assert _content_id(calls, "agent_memory_ok") == "cid-X"


def test_failure_path_links_content_id_when_draft_created():
    # narración falló pero el draft existe → el failure path lo enlaza igual
    calls = _run_uam((None, ClaudeError("timeout", "cayó"), ["cid-Y"]))
    assert _content_id(calls, "agent_memory_failed") == "cid-Y"


def test_no_draft_content_id_is_none():
    calls = _run_uam(("reply", None, []))
    assert _content_id(calls, "agent_memory_ok") is None
