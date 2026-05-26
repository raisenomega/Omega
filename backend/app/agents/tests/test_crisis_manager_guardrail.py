"""Regresión P4/AS-R2: el crisis manager NUNCA publica solo (regla INVIOLABLE).

`ACCIONES_PROHIBIDAS` (limits_omega) ahora se enforza en CrisisManagerAgent: cualquier task
con una acción pública prohibida (respond_to_complaint_publicly, post_apology_for_crisis)
lanza PermissionError. El agente solo produce drafts marcados como requires_human_approval.
Estos tests FALLAN si alguien quita el guardrail, expone una vía de auto-publish, o
hardcodea el model fuera de la routing_table (I2).
"""
import asyncio
import pytest
from app.agents.crisis_manager_agent import CrisisManagerAgent
from app.bc_cognition.domain.routing_table import resolve_model


def test_blocks_respond_to_complaint_publicly():
    agent = CrisisManagerAgent()
    with pytest.raises(PermissionError):
        agent._assert_human_in_the_loop("respond_to_complaint_publicly")


def test_blocks_post_apology_for_crisis():
    agent = CrisisManagerAgent()
    with pytest.raises(PermissionError):
        agent._assert_human_in_the_loop("post_apology_for_crisis")


def test_allows_non_publish_actions():
    agent = CrisisManagerAgent()
    agent._assert_human_in_the_loop("assess")  # no lanza
    agent._assert_human_in_the_loop(None)       # no lanza


def test_execute_blocks_prohibited_action():
    agent = CrisisManagerAgent()
    with pytest.raises(PermissionError):
        asyncio.run(agent.execute({"type": "draft_statement", "action": "respond_to_complaint_publicly"}))


def test_never_autonomously_publishes():
    assert CrisisManagerAgent.AUTONOMOUS_PUBLISH_ALLOWED is False


def test_model_from_routing_table_not_hardcoded():
    agent = CrisisManagerAgent()
    assert agent.model == resolve_model("crisis_manager")
    assert agent.model == "claude-opus-4-7"  # opus · ID válido (no el inválido 'claude-opus-4')
