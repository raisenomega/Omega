"""DEBT-067: verificar que cada agente envía el model correcto a la API de Anthropic.

X2: tests que confirman el effective_model enviado al cliente Anthropic por
generate_text() para al menos dos agentes representativos:
  - crisis_manager  → opus  (claude-opus-4-7)
  - analytics       → sonnet (claude-sonnet-4-6)

El patch se hace en TEST exclusivamente (los test files son exentos del
no-mock check per guardrail G9).  El código de producción no contiene mocks.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _fake_message(text: str = "ok"):
    """Minimal Anthropic Message stub."""
    content_block = MagicMock()
    content_block.text = text
    msg = MagicMock()
    msg.content = [content_block]
    return msg


# ---------------------------------------------------------------------------
# test_crisis_manager_uses_opus
# ---------------------------------------------------------------------------

def test_crisis_manager_uses_opus():
    """generate_text recibe model=claude-opus-4-7 cuando el agente es crisis_manager."""
    from app.agents.crisis_manager_agent import CrisisManagerAgent
    from app.bc_cognition.domain.routing_table import resolve_model
    from app.services.crisis_detector import CrisisSignals

    agent = CrisisManagerAgent()
    assert agent.model == "claude-opus-4-7", (
        f"Expected claude-opus-4-7, got {agent.model}"
    )
    assert agent.model == resolve_model("crisis_manager")

    captured_models = []

    async def _fake_create(**kwargs):
        captured_models.append(kwargs.get("model"))
        return _fake_message("crisis analysis ok")

    signals = CrisisSignals(
        platform="instagram",
        negative_comment_percentage=0.2,
        complaint_velocity=1.0,
        sentiment_drop=0.0,
        media_involvement=False,
        influencer_involvement=False,
        reach_of_negative_content=100,
    )

    with patch(
        "app.infrastructure.ai.claude_service.claude_service.client"
    ) as mock_client:
        mock_client.messages.create = AsyncMock(side_effect=_fake_create)
        asyncio.run(agent.assess_crisis(signals))

    assert len(captured_models) >= 1, "generate_text was never called"
    for m in captured_models:
        assert m == "claude-opus-4-7", (
            f"Crisis manager sent wrong model to API: {m}"
        )


# ---------------------------------------------------------------------------
# test_analytics_agent_uses_sonnet
# ---------------------------------------------------------------------------

def test_analytics_agent_uses_sonnet():
    """generate_text recibe model=claude-sonnet-4-6 cuando el agente es analytics."""
    from app.agents.analytics_agent import AnalyticsAgent
    from app.bc_cognition.domain.routing_table import resolve_model

    agent = AnalyticsAgent()
    assert agent.model == "claude-sonnet-4-6", (
        f"Expected claude-sonnet-4-6, got {agent.model}"
    )
    assert agent.model == resolve_model("analytics")

    captured_models = []

    async def _fake_create(**kwargs):
        captured_models.append(kwargs.get("model"))
        return _fake_message("insights ok")

    with patch(
        "app.infrastructure.ai.claude_service.claude_service.client"
    ) as mock_client:
        mock_client.messages.create = AsyncMock(side_effect=_fake_create)

        asyncio.run(
            agent._analyze_metrics(
                {
                    "data": {
                        "likes": 100,
                        "comments": 20,
                        "shares": 10,
                        "followers": 1000,
                        "impressions": 5000,
                    }
                }
            )
        )

    assert len(captured_models) >= 1, "generate_text was never called"
    for m in captured_models:
        assert m == "claude-sonnet-4-6", (
            f"Analytics agent sent wrong model to API: {m}"
        )


# ---------------------------------------------------------------------------
# test_generate_text_fallback_to_self_model
# ---------------------------------------------------------------------------

def test_generate_text_no_model_arg_uses_service_default():
    """Backward compat: callers sin arg model siguen usando self.model del service."""
    import asyncio
    from app.infrastructure.ai.claude_service import ClaudeService

    service = ClaudeService()
    assert service.model == "claude-sonnet-4-6"

    captured_models = []

    async def _fake_create(**kwargs):
        captured_models.append(kwargs.get("model"))
        return _fake_message("fallback ok")

    with patch.object(service, "client") as mock_client:
        mock_client.messages.create = AsyncMock(side_effect=_fake_create)
        asyncio.run(service.generate_text(prompt="hello"))

    assert captured_models == ["claude-sonnet-4-6"], (
        f"Fallback model wrong: {captured_models}"
    )


# ---------------------------------------------------------------------------
# test_generate_text_model_override
# ---------------------------------------------------------------------------

def test_generate_text_model_override_used():
    """El parametro model= de generate_text tiene precedencia sobre self.model."""
    import asyncio
    from app.infrastructure.ai.claude_service import ClaudeService

    service = ClaudeService()  # self.model = sonnet

    captured_models = []

    async def _fake_create(**kwargs):
        captured_models.append(kwargs.get("model"))
        return _fake_message("override ok")

    with patch.object(service, "client") as mock_client:
        mock_client.messages.create = AsyncMock(side_effect=_fake_create)
        asyncio.run(
            service.generate_text(prompt="hello", model="claude-opus-4-7")
        )

    assert captured_models == ["claude-opus-4-7"], (
        f"Model override not applied: {captured_models}"
    )
