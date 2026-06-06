"""Fase 1 commit 2 · agent_registry deriva de canonical_agents.
Alias legacy → code canónico → model real. Firma intacta (dispatcher no cambia)."""
import pytest

from app.infrastructure.ai.agent_registry import (
    get_agent_config, is_agent_registered, get_total_agent_count,
)


def test_alias_resolves_to_real_model():
    assert get_agent_config("ATLAS")["model"] == "claude-sonnet-4-6"       # strategy
    assert get_agent_config("@RAFA")["model"] == "claude-sonnet-4-6"       # content_creator
    assert get_agent_config("KIRA")["model"] == "claude-sonnet-4-6"        # engagement (resolve_model)
    assert get_agent_config("NOVA")["model"] == "claude-opus-4-7"          # corrige sonnet→opus
    assert get_agent_config("SENTINEL")["model"] == "claude-opus-4-7"      # sentinel_security


def test_provider_always_anthropic():
    for name in ("ATLAS", "RAFA", "KIRA", "NOVA", "SENTINEL", "GUARD", "@rafa"):
        assert get_agent_config(name)["provider"] == "anthropic"


def test_is_registered_active_vs_inactive():
    assert is_agent_registered("ATLAS") is True
    assert is_agent_registered("VERA") is False   # inactive → dispatcher hace fallback NOVA


def test_inactive_raises_keyerror():
    with pytest.raises(KeyError):
        get_agent_config("VERA")


def test_total_count_is_8():
    assert get_total_agent_count() == 8
