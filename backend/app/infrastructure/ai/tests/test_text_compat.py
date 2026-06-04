"""Tests del bridge _text_compat (DEBT-024).

Convencion del repo: tests async via asyncio.run() en funcion sync
(ver test_model_routing_propagation.py). El adapter es async -> AsyncMock.
"""
import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.infrastructure.ai import _text_compat


class FakeResponse:
    def __init__(self, text: str):
        self.text = text


class FakeError:
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


def test_generate_text_happy_path():
    """Devuelve string y preserva defaults legacy cuando adapter retorna (response, None)."""
    fake = AsyncMock(return_value=(FakeResponse("hello world"), None))
    with patch.object(_text_compat, "_adapter_generate", fake):
        result = asyncio.run(
            _text_compat.generate_text(agent_code="growth_hacker", prompt="say hi")
        )

    assert result == "hello world"
    fake.assert_awaited_once()
    kwargs = fake.call_args.kwargs
    assert kwargs["agent_code"] == "growth_hacker"
    assert kwargs["system"] == ""            # default None -> ""
    assert kwargs["temperature"] == 0.7      # default legacy preservado
    assert kwargs["max_tokens"] == 4096      # default legacy preservado
    assert kwargs["messages"] == [{"role": "user", "content": "say hi"}]


def test_generate_text_with_system_message():
    """system_message y overrides de temperature/max_tokens se pasan al adapter."""
    fake = AsyncMock(return_value=(FakeResponse("ok"), None))
    with patch.object(_text_compat, "_adapter_generate", fake):
        asyncio.run(
            _text_compat.generate_text(
                agent_code="brand_voice",
                prompt="test",
                system_message="You are X.",
                temperature=0.5,
                max_tokens=2048,
            )
        )

    kwargs = fake.call_args.kwargs
    assert kwargs["system"] == "You are X."
    assert kwargs["temperature"] == 0.5
    assert kwargs["max_tokens"] == 2048


def test_generate_text_raises_on_error():
    """Preserva el contract raise-on-error de claude_service legacy."""
    fake = AsyncMock(return_value=(None, FakeError("rate_limited", "Too many requests")))
    with patch.object(_text_compat, "_adapter_generate", fake):
        with pytest.raises(RuntimeError) as exc_info:
            asyncio.run(
                _text_compat.generate_text(agent_code="growth_hacker", prompt="test")
            )

    assert "rate_limited" in str(exc_info.value)
    assert "Too many requests" in str(exc_info.value)
