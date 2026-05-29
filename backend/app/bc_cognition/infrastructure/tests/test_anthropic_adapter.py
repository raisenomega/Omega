"""Red de seguridad del adapter (Fase 1 · PASO 1a) · fotografía generate() ACTUAL.

NO modifica el adapter · captura su comportamiento de hoy para que 1b (tool-calling)
no rompa lo que funciona. messages.create se mockea (cero llamadas reales a Anthropic).
Patrón: AsyncMock + asyncio.run (como test_model_routing_propagation). G9 exime tests.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.bc_cognition.infrastructure import anthropic_adapter as ad


def _fake_message(text="hola", in_tok=10, out_tok=5, cache_read=0):
    """Stub mínimo de un Anthropic Message."""
    block = MagicMock(); block.type = "text"; block.text = text
    msg = MagicMock()
    msg.content = [block]
    msg.usage = MagicMock(input_tokens=in_tok, output_tokens=out_tok,
                          cache_read_input_tokens=cache_read)
    return msg


def _patch_client(monkeypatch, create_mock):
    """Inyecta un cliente fake cuyo .messages.create es create_mock. Resetea singleton."""
    ad._client = None
    client = MagicMock()
    client.messages = MagicMock(); client.messages.create = create_mock
    monkeypatch.setattr(ad, "_get_client", lambda: client)
    return client


def test_generate_returns_text_from_content(monkeypatch):
    create = AsyncMock(return_value=_fake_message(text="respuesta"))
    _patch_client(monkeypatch, create)
    resp, err = asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "hi"}]))
    assert err is None
    assert resp is not None and resp.text == "respuesta"


def test_generate_passes_cache_control_system_block(monkeypatch):
    create = AsyncMock(return_value=_fake_message())
    _patch_client(monkeypatch, create)
    asyncio.run(ad.generate("aria_1", "mi-sistema", [{"role": "user", "content": "hi"}]))
    kwargs = create.call_args.kwargs
    assert kwargs["system"] == [
        {"type": "text", "text": "mi-sistema", "cache_control": {"type": "ephemeral"}}
    ]


def test_generate_passes_model_params_and_no_tools(monkeypatch):
    create = AsyncMock(return_value=_fake_message())
    _patch_client(monkeypatch, create)
    asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "hi"}],
                            max_tokens=512, temperature=0.5))
    kwargs = create.call_args.kwargs
    assert kwargs["model"] == ad.resolve_model("aria_1")
    assert kwargs["max_tokens"] == 512 and kwargs["temperature"] == 0.5
    assert kwargs["messages"] == [{"role": "user", "content": "hi"}]
    assert "tools" not in kwargs  # ANCLA 1b: hoy NO hay tools · 1b lo cambia conscientemente


def test_generate_invalid_agent_code_returns_error(monkeypatch):
    create = AsyncMock(return_value=_fake_message())
    _patch_client(monkeypatch, create)
    resp, err = asyncio.run(ad.generate("agente_inexistente", "sys", [{"role": "user", "content": "x"}]))
    assert resp is None
    assert err is not None and err.code == "invalid_input"
    create.assert_not_called()  # no llega a la API si el agent_code es inválido


def test_generate_timeout_returns_error(monkeypatch):
    create = AsyncMock(side_effect=asyncio.TimeoutError())
    _patch_client(monkeypatch, create)
    resp, err = asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "x"}]))
    assert resp is None
    assert err is not None and err.code == "timeout"


def test_generate_computes_usage_and_cache_hit(monkeypatch):
    create = AsyncMock(return_value=_fake_message(in_tok=100, out_tok=20, cache_read=80))
    _patch_client(monkeypatch, create)
    resp, err = asyncio.run(ad.generate("aria_1", "sys", [{"role": "user", "content": "x"}]))
    assert err is None and resp is not None
    assert resp.input_tokens == 100 and resp.output_tokens == 20
    assert resp.cache_hit is True
