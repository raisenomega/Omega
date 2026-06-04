"""Test X2 · persona_nova refleja la jerarquia canonica (OMEGA_ROLES_CANONICO §2).

DEBT-ROLES-001 · enhancement ritual X2 (4 jun 2026): NOVA afirma la arquitectura
operativa real (8 agentes operativos + SOPHIA + GUARDIAN) y aclara que ARIA es su
cara publica, no un agente del catalogo. Cero numero falso (37/45).
"""
from app.bc_cognition.domain.persona_nova import NOVA_SYSTEM_PROMPT


def test_persona_nova_mentions_8_operative_agents():
    assert "8 agentes operativos" in NOVA_SYSTEM_PROMPT


def test_persona_nova_mentions_sophia():
    assert "SOPHIA" in NOVA_SYSTEM_PROMPT


def test_persona_nova_mentions_guardian():
    assert "GUARDIAN" in NOVA_SYSTEM_PROMPT


def test_persona_nova_clarifies_aria_role():
    assert "ARIA es tu cara pública" in NOVA_SYSTEM_PROMPT


def test_persona_nova_no_false_agent_count():
    assert "37 agentes" not in NOVA_SYSTEM_PROMPT
    assert "45 agentes" not in NOVA_SYSTEM_PROMPT
