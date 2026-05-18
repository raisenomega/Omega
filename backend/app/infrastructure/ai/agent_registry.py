"""
Agent Registry - Maps 45 OMEGA agents to AI providers and models.
DDD: Infrastructure layer - Agent-to-Provider mapping.
Max 200L strict. Type-safe, no `any`.
"""
from typing import Dict, TypedDict, Literal
from enum import Enum


class Department(str, Enum):
    """Department enum for organizational structure."""
    EXECUTIVE = "EXECUTIVE"
    MARKETING = "MARKETING"
    PRODUCT = "PRODUCT"
    OPERATIONS = "OPERATIONS"
    FINANCE = "FINANCE"
    COMMUNITY = "COMMUNITY"
    INTELLIGENCE = "INTELLIGENCE"
    PEOPLE = "PEOPLE"
    SECURITY = "SECURITY"


# Type-safe provider literals (Fase 2 §2.6: solo anthropic permitido · I1)
ProviderName = Literal["anthropic"]


class AgentConfig(TypedDict):
    """
    Type-safe agent configuration.
    Zero `any` types - complete type safety.
    """
    provider: ProviderName
    model: str
    department: Department


# Complete OMEGA Agent Registry - 45 Agents
AGENT_REGISTRY: Dict[str, AgentConfig] = {
    # EXECUTIVE (1 agent)
    "NOVA": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",
        "department": Department.EXECUTIVE
    },

    # MARKETING (6 agents) - GPT-4o-mini
    "ATLAS": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.MARKETING},
    "RAFA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.MARKETING},
    "DUDA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.MARKETING},
    "ECHO": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.MARKETING},
    "LUAN": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.MARKETING},
    "PIXEL": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.MARKETING},

    # PRODUCT & TECHNOLOGY (5 agents) - Deepseek Chat
    "LUNA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PRODUCT},
    "SHIELD": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PRODUCT},
    "FORGE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PRODUCT},
    "DEBUG": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PRODUCT},
    "SCOPE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PRODUCT},

    # OPERATIONS (5 agents) - GPT-4o-mini (cost-efficient)
    "REX": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.OPERATIONS},
    "ANCHOR": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.OPERATIONS},
    "BRIDGE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.OPERATIONS},
    "FLOW": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.OPERATIONS},
    "SCOUT": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.OPERATIONS},

    # FINANCE (5 agents) - Gemini 2.0 Flash
    "VERA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.FINANCE},
    "LEDGER": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.FINANCE},
    "PULSE_FIN": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.FINANCE},
    "QUOTA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.FINANCE},
    "MARGIN": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.FINANCE},

    # COMMUNITY (5 agents) - Groq Llama 3.3 (ultra-fast)
    "KIRA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.COMMUNITY},
    "REVIEW": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.COMMUNITY},
    "NURTURE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.COMMUNITY},
    "TRIBE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.COMMUNITY},
    "VOICE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.COMMUNITY},

    # INTELLIGENCE (5 agents) - Deepseek R1 Reasoner
    "ORACLE": {"provider": "anthropic", "model": "claude-opus-4-7", "department": Department.INTELLIGENCE},
    "TREND": {"provider": "anthropic", "model": "claude-opus-4-7", "department": Department.INTELLIGENCE},
    "SIGNAL": {"provider": "anthropic", "model": "claude-opus-4-7", "department": Department.INTELLIGENCE},
    "MAP": {"provider": "anthropic", "model": "claude-opus-4-7", "department": Department.INTELLIGENCE},
    "LENS": {"provider": "anthropic", "model": "claude-opus-4-7", "department": Department.INTELLIGENCE},

    # PEOPLE (5 agents) - GPT-4o-mini
    "SOPHIA": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PEOPLE},
    "HIRE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PEOPLE},
    "TRAIN": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PEOPLE},
    "CULTURE": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PEOPLE},
    "COMPASS": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "department": Department.PEOPLE},

    # SECURITY (13 agents) - GPT-4o
    "SENTINEL": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "VAULT": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "PULSE_MON": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "GUARD": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "WATCH": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "LOCK": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "TRACE": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "AUDIT": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "SHIELD_SEC": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "CIPHER": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "PERIMETER": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "RESPONSE": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
    "SCAN": {"provider": "anthropic", "model": "claude-sonnet-4-6", "department": Department.SECURITY},
}


def get_agent_config(agent_code: str) -> AgentConfig:
    """
    Get agent configuration by code.

    Args:
        agent_code: Agent code (e.g., "NOVA", "ATLAS")

    Returns:
        AgentConfig with provider, model, department

    Raises:
        KeyError: If agent not found in registry
    """
    agent_upper = agent_code.upper().strip()
    if agent_upper not in AGENT_REGISTRY:
        raise KeyError(
            f"Agent '{agent_code}' not found in registry. "
            f"Valid agents: {', '.join(sorted(AGENT_REGISTRY.keys()))}"
        )
    return AGENT_REGISTRY[agent_upper]


def is_agent_registered(agent_code: str) -> bool:
    """Check if agent exists in registry."""
    return agent_code.upper().strip() in AGENT_REGISTRY


def get_agents_by_department(department: Department) -> Dict[str, AgentConfig]:
    """Get all agents in a department."""
    return {
        code: config
        for code, config in AGENT_REGISTRY.items()
        if config["department"] == department
    }


def get_agents_by_provider(provider: ProviderName) -> Dict[str, AgentConfig]:
    """Get all agents using a specific provider."""
    return {
        code: config
        for code, config in AGENT_REGISTRY.items()
        if config["provider"] == provider
    }


def get_total_agent_count() -> int:
    """Get total number of registered agents."""
    return len(AGENT_REGISTRY)
