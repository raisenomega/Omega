"""A1.1 · tool_choice en el adapter: forzar tool-use (guion N placas garantizado vía input_schema).
Separado de test_anthropic_adapter.py por el ratchet C4 (≤100L · aquel ya estaba en 98). Mismo patrón:
ai_provider_execute mockeado (cero API real). G9 exime tests."""
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.bc_cognition.infrastructure import anthropic_adapter as ad


def _fake_message(tool_use=False):
    block = MagicMock(); block.type = "text"; block.text = "ok"
    content = [block]
    if tool_use:
        tu = MagicMock(); tu.type = "tool_use"; tu.name = "x"; tu.input = {}
        content.append(tu)
    msg = MagicMock(); msg.content = content
    msg.usage = MagicMock(input_tokens=10, output_tokens=5, cache_read_input_tokens=0)
    return msg


def _patch(monkeypatch, execute_mock):
    monkeypatch.setattr(ad, "ai_provider_execute", execute_mock)
    monkeypatch.setattr(ad, "record_mcp_use", lambda *a, **k: None)


def test_tool_choice_llega_a_create_kwargs(monkeypatch):  # forzar tool-use → la clave llega al provider
    execute = AsyncMock(return_value=_fake_message())
    _patch(monkeypatch, execute)
    tc = {"type": "tool", "name": "x"}
    asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "hi"}], tool_choice=tc))
    assert execute.call_args.args[0]["tool_choice"] == tc


def test_sin_tool_choice_no_se_pasa(monkeypatch):  # retrocompat byte-idéntica (espeja `tools` None)
    execute = AsyncMock(return_value=_fake_message())
    _patch(monkeypatch, execute)
    asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "hi"}]))
    assert "tool_choice" not in execute.call_args.args[0]


def test_round_trip_tool_forzado(monkeypatch):  # tool_choice forzado + tools → tool_use parseado de vuelta
    execute = AsyncMock(return_value=_fake_message(tool_use=True))
    _patch(monkeypatch, execute)
    tools = [{"name": "x", "description": "d", "input_schema": {}}]
    resp, err = asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "hi"}],
                                        tools=tools, tool_choice={"type": "tool", "name": "x"}))
    assert err is None and resp is not None
    assert resp.tool_calls is not None and resp.tool_calls[0].type == "tool_use"
