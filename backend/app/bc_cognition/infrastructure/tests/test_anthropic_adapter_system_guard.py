"""DEBT-024 · guard cache_control en system vacío.

Anthropic rechaza (400) un text block vacío con cache_control. La ruta real de
generate() es ai_provider_execute (Capa 7-A), no _get_client → se mockea esa.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.bc_cognition.infrastructure import anthropic_adapter as ad


def _fake_msg():
    block = MagicMock(); block.type = "text"; block.text = "ok"
    msg = MagicMock(); msg.content = [block]
    msg.usage = MagicMock(input_tokens=10, output_tokens=5, cache_read_input_tokens=0)
    return msg


def _patch_execute(monkeypatch, exec_mock):
    monkeypatch.setattr(ad, "ai_provider_execute", exec_mock)
    monkeypatch.setattr(ad, "record_mcp_use", lambda *a, **k: None)


def test_generate_empty_system_omits_cache_control_block(monkeypatch):
    """system='' NO debe ir como text block vacío con cache_control."""
    execute = AsyncMock(return_value=_fake_msg())
    _patch_execute(monkeypatch, execute)
    asyncio.run(ad.generate("content_creator", "", [{"role": "user", "content": "hi"}]))
    assert "system" not in execute.call_args.args[0]


def test_generate_nonempty_system_keeps_cache_control(monkeypatch):
    """system no-vacío preserva el bloque cache_control ephemeral (I3)."""
    execute = AsyncMock(return_value=_fake_msg())
    _patch_execute(monkeypatch, execute)
    asyncio.run(ad.generate("content_creator", "mi-sistema", [{"role": "user", "content": "hi"}]))
    assert execute.call_args.args[0]["system"] == [
        {"type": "text", "text": "mi-sistema", "cache_control": {"type": "ephemeral"}}
    ]
