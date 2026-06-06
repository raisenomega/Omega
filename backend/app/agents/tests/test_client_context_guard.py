"""GAP-3 · client_context: merge no-destructivo + chain read-only.
TDD: el contexto curado del cliente NUNCA se pisa ni se NULLea (P1/P2)."""
import asyncio
from unittest.mock import MagicMock

from app.agents.client_context_agent import ClientContextAgent
from app.agents.orchestrator_agent import OrchestratorAgent


# ── CAMBIO 2 · merge no-destructivo en _save_context (_fill_if_empty) ──
def test_curated_value_preserved_over_llm():
    assert ClientContextAgent._fill_if_empty("Mantenimiento limpieza", "otra cosa") == "Mantenimiento limpieza"
    assert ClientContextAgent._fill_if_empty(["curado"], ["llm"]) == ["curado"]


def test_empty_field_filled_by_llm():
    assert ClientContextAgent._fill_if_empty(None, "valor") == "valor"
    assert ClientContextAgent._fill_if_empty("", "valor") == "valor"
    assert ClientContextAgent._fill_if_empty([], ["x"]) == ["x"]
    assert ClientContextAgent._fill_if_empty({}, {"k": "v"}) == {"k": "v"}


def test_llm_none_or_empty_does_not_null_curated():
    assert ClientContextAgent._fill_if_empty("curado", None) == "curado"
    assert ClientContextAgent._fill_if_empty("curado", "") == "curado"
    assert ClientContextAgent._fill_if_empty(["curado"], []) == ["curado"]


# ── CAMBIO 1 · el nodo client_context del chain es READ-ONLY (no LLM, no write) ──
def test_chain_client_context_node_is_readonly():
    orch = OrchestratorAgent(lazy=True)
    orch.context_repo = MagicMock()
    orch.context_repo.find_by_client_id.return_value = MagicMock(
        niche="Mantenimiento limpieza", tone="casual", brand_voice={},
        target_audience="hogares", content_themes=[], preferred_formats=[])
    orch.client_context_agent = MagicMock()
    orch.agent_repo = MagicMock()
    asyncio.run(orch._execute_chain(["client_context"], "client-123", {}))
    orch.context_repo.find_by_client_id.assert_called_with("client-123")  # LEE el curado
    orch.client_context_agent.execute.assert_not_called()                 # NO ejecuta LLM
    orch.context_repo.upsert.assert_not_called()                          # NO escribe


# ── GAP-1 · toda CHAIN despacha a codes canónicos REALES (ningún nodo cae a fallback NOVA) ──
def test_all_chains_dispatch_to_registered_agents():
    from app.infrastructure.ai.agent_registry import is_agent_registered

    for trigger, chain in OrchestratorAgent.CHAINS.items():
        for node in chain:
            if node == "client_context":   # nodo read-only (GAP-3), no se despacha
                continue
            assert is_agent_registered(node), (
                f"CHAIN '{trigger}' despacha '{node}' que NO es code canónico (caería a fallback NOVA)"
            )
