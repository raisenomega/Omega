"""
Agent Registry - Resuelve agent codes/alias a config (provider/model/department).
Fuente única de identidad: bc_cognition/domain/canonical_agents (8 + SOPHIA + GUARDIAN).
Los nombres legacy (ATLAS, RAFA...) son alias→code canónico. Type-safe, no `any`.
DDD: Infrastructure layer.
"""
from typing import Dict, TypedDict, Literal
from enum import Enum

from app.bc_cognition.domain.canonical_agents import (
    resolve_alias, CANONICAL_AGENTS, operational_count,
)
from app.bc_cognition.domain.routing_table import resolve_model


class Department(str, Enum):
    """Department enum for organizational structure (metadata · sin consumidores runtime)."""
    EXECUTIVE = "EXECUTIVE"
    MARKETING = "MARKETING"
    PRODUCT = "PRODUCT"
    OPERATIONS = "OPERATIONS"
    FINANCE = "FINANCE"
    COMMUNITY = "COMMUNITY"
    INTELLIGENCE = "INTELLIGENCE"
    PEOPLE = "PEOPLE"
    SECURITY = "SECURITY"


# Type-safe provider literals (Fase 2 §2.6: solo anthropic · I1)
ProviderName = Literal["anthropic"]


class AgentConfig(TypedDict):
    """Type-safe agent configuration. Zero `any`."""
    provider: ProviderName
    model: str
    department: Department


# Department por code (metadata no-crítica · default EXECUTIVE).
_DEPARTMENT: Dict[str, Department] = {
    "nova_chat": Department.EXECUTIVE,
    "orchestrator": Department.EXECUTIVE,
    "sophia": Department.EXECUTIVE,
    "content_creator": Department.MARKETING,
    "strategy": Department.MARKETING,
    "brand_voice": Department.MARKETING,
    "engagement": Department.COMMUNITY,
    "analytics": Department.INTELLIGENCE,
    "crisis_manager": Department.OPERATIONS,
    "sentinel_security": Department.SECURITY,
    "guardian": Department.SECURITY,
}


def get_agent_config(agent_code: str) -> AgentConfig:
    """
    Resuelve alias/code → AgentConfig (provider/model/department).

    Args:
        agent_code: code canónico o nombre legacy (e.g. "ATLAS", "@RAFA", "nova_chat").

    Returns:
        AgentConfig con provider="anthropic", model resuelto, department metadata.

    Raises:
        KeyError: si el code/alias no resuelve a un agente operativo (inactive/desconocido).
    """
    target = resolve_alias(agent_code)
    if target is None:
        raise KeyError(f"Agent '{agent_code}' not operational/registered")
    model = (
        CANONICAL_AGENTS[target]["model"]
        if target in CANONICAL_AGENTS
        else resolve_model(target)
    )
    return AgentConfig(
        provider="anthropic",
        model=model,
        department=_DEPARTMENT.get(target, Department.EXECUTIVE),
    )


def is_agent_registered(agent_code: str) -> bool:
    """True si el code/alias resuelve a un agente operativo (False para INACTIVE/desconocido)."""
    return resolve_alias(agent_code) is not None


def get_agents_by_department(department: Department) -> Dict[str, AgentConfig]:
    """Agentes canónicos en un departamento (metadata · sin consumidores runtime)."""
    return {
        code: get_agent_config(code)
        for code in CANONICAL_AGENTS
        if _DEPARTMENT.get(code, Department.EXECUTIVE) == department
    }


def get_agents_by_provider(provider: ProviderName) -> Dict[str, AgentConfig]:
    """Agentes canónicos por provider (todos anthropic · I1)."""
    if provider != "anthropic":
        return {}
    return {code: get_agent_config(code) for code in CANONICAL_AGENTS}


def get_total_agent_count() -> int:
    """Número de agentes operativos canónicos (= 8)."""
    return operational_count()
