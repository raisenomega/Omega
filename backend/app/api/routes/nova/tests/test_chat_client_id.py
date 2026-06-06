"""SUB-PASO 2.0 · client_id explícito (Switcher) gana sobre el nombre del texto (anti-eco-ARIA).
Validación de EXISTENCIA (NOVA owner-only). Mockea reader + route_to_agent + get_client_context."""
import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.routes.nova.handlers import chat as chat_mod
from app.api.routes.nova.handlers._chat_helpers import ChatRequest, ChatMessage


def _req(content: str, client_id=None) -> ChatRequest:
    return ChatRequest(messages=[ChatMessage(role="user", content=content)], client_id=client_id)


# ── 1 · ChatRequest acepta client_id opcional (ausente por default) ──
def test_chatrequest_client_id_optional():
    assert _req("hola").client_id is None
    assert _req("hola", client_id="abc").client_id == "abc"


# ── 2 · id explícito GANA sobre un nombre distinto en el texto ──
def test_explicit_client_id_wins_over_name():
    rt = AsyncMock(return_value={"role": "assistant", "content": "ok"})
    with patch.object(chat_mod.clients_reader, "get_client",
                      return_value={"id": "ZID-EXPLICIT", "name": "Zafacones"}), \
         patch.object(chat_mod, "route_to_agent", rt), \
         patch.object(chat_mod, "get_client_context",
                      AsyncMock(return_value=("OtroNegocio", "WRONG-ID", "ctx"))):
        asyncio.run(chat_mod.handle_chat(
            _req("@RAFA escribí un post. trabajamos con OtroNegocio", client_id="ZID-EXPLICIT")))
    assert rt.called
    assert rt.call_args.kwargs["client_id"] == "ZID-EXPLICIT"  # el id del texto (WRONG-ID) se ignora


# ── 3 · sin client_id → fallback por nombre del texto (no regresión) ──
def test_fallback_by_name_when_no_client_id():
    rt = AsyncMock(return_value={"role": "assistant", "content": "ok"})
    with patch.object(chat_mod, "route_to_agent", rt), \
         patch.object(chat_mod, "get_client_context",
                      AsyncMock(return_value=("Zafacones", "ZID-BYNAME", "ctx"))):
        asyncio.run(chat_mod.handle_chat(_req("@RAFA dale. trabajamos con Zafacones")))
    assert rt.call_args.kwargs["client_id"] == "ZID-BYNAME"


# ── 4 · client_id inexistente → 404 client_not_found ──
def test_nonexistent_client_id_raises_404():
    with patch.object(chat_mod.clients_reader, "get_client", return_value=None):
        try:
            asyncio.run(chat_mod.handle_chat(_req("hola", client_id="bad-uuid")))
            assert False, "esperaba HTTPException 404"
        except HTTPException as e:
            assert e.status_code == 404 and e.detail == "client_not_found"
