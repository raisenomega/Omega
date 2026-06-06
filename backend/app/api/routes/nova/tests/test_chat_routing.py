"""Fase 1 commit 3 · chat.py resuelve @mención legacy → code canónico antes del dispatch.
Mockea route_to_agent (no llama Anthropic). Inactivos → respuesta honesta, no dispatch."""
import asyncio
from unittest.mock import AsyncMock, patch

from app.api.routes.nova.handlers import chat as chat_mod
from app.api.routes.nova.handlers._chat_helpers import ChatRequest, ChatMessage


def _req(content: str) -> ChatRequest:
    return ChatRequest(messages=[ChatMessage(role="user", content=content)])


def _routed_code(content: str):
    """Devuelve (code, system_prompt) que recibió route_to_agent, o None si no se llamó."""
    rt = AsyncMock(return_value={"role": "assistant", "content": "ok"})
    with patch.object(chat_mod, "route_to_agent", rt):
        asyncio.run(chat_mod.handle_chat(_req(content)))
    if rt.called:
        return rt.call_args.args[0], rt.call_args.args[2]  # code, system_prompt
    return None


def test_atlas_routes_to_strategy():
    code, sysp = _routed_code("@ATLAS analizá tendencias")
    assert code == "strategy"
    assert "STRATEGY" in sysp and "OMEGA Company" not in sysp  # role real, no genérico


def test_rafa_routes_to_content_creator():
    assert _routed_code("@RAFA escribí un post")[0] == "content_creator"


def test_kira_routes_to_engagement():
    assert _routed_code("@KIRA respondé el comentario")[0] == "engagement"


def test_sentinel_routes_to_sentinel_security():
    assert _routed_code("@SENTINEL revisá la seguridad")[0] == "sentinel_security"


def test_inactive_vera_returns_honest_no_dispatch():
    rt = AsyncMock()
    with patch.object(chat_mod, "route_to_agent", rt):
        out = asyncio.run(chat_mod.handle_chat(_req("@VERA armá el reporte financiero")))
    rt.assert_not_called()
    assert "no está" in out["content"] and "operativo" in out["content"]


def test_no_mention_does_not_route():
    rt = AsyncMock()
    with patch.object(chat_mod, "route_to_agent", rt):
        try:
            asyncio.run(chat_mod.handle_chat(_req("hola, listo para trabajar")))
        except Exception:
            pass  # NOVA path puede fallar con key dummy · irrelevante para este assert
    rt.assert_not_called()
