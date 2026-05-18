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


# Type-safe provider literals (no string guessing)
ProviderName = Literal["anthropic", "openai", "deepseek", "gemini", "groq"]


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
        "model": "claude-sonnet-4-5-20250929",
        "department": Department.EXECUTIVE
    },

    # MARKETING (6 agents) - GPT-4o-mini
    "ATLAS": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.MARKETING},
    "RAFA": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.MARKETING},
    "DUDA": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.MARKETING},
    "ECHO": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.MARKETING},
    "LUAN": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.MARKETING},
    "PIXEL": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.MARKETING},

    # PRODUCT & TECHNOLOGY (5 agents) - Deepseek Chat
    "LUNA": {"provider": "deepseek", "model": "deepseek-chat", "department": Department.PRODUCT},
    "SHIELD": {"provider": "deepseek", "model": "deepseek-chat", "department": Department.PRODUCT},
    "FORGE": {"provider": "deepseek", "model": "deepseek-chat", "department": Department.PRODUCT},
    "DEBUG": {"provider": "deepseek", "model": "deepseek-chat", "department": Department.PRODUCT},
    "SCOPE": {"provider": "deepseek", "model": "deepseek-chat", "department": Department.PRODUCT},

    # OPERATIONS (5 agents) - GPT-4o-mini (cost-efficient)
    "REX": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.OPERATIONS},
    "ANCHOR": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.OPERATIONS},
    "BRIDGE": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.OPERATIONS},
    "FLOW": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.OPERATIONS},
    "SCOUT": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.OPERATIONS},

    # FINANCE (5 agents) - Gemini 2.0 Flash
    "VERA": {"provider": "gemini", "model": "gemini-2.0-flash-exp", "department": Department.FINANCE},
    "LEDGER": {"provider": "gemini", "model": "gemini-2.0-flash-exp", "department": Department.FINANCE},
    "PULSE_FIN": {"provider": "gemini", "model": "gemini-2.0-flash-exp", "department": Department.FINANCE},
    "QUOTA": {"provider": "gemini", "model": "gemini-2.0-flash-exp", "department": Department.FINANCE},
    "MARGIN": {"provider": "gemini", "model": "gemini-2.0-flash-exp", "department": Department.FINANCE},

    # COMMUNITY (5 agents) - Groq Llama 3.3 (ultra-fast)
    "KIRA": {"provider": "groq", "model": "llama-3.3-70b-versatile", "department": Department.COMMUNITY},
    "REVIEW": {"provider": "groq", "model": "llama-3.3-70b-versatile", "department": Department.COMMUNITY},
    "NURTURE": {"provider": "groq", "model": "llama-3.3-70b-versatile", "department": Department.COMMUNITY},
    "TRIBE": {"provider": "groq", "model": "llama-3.3-70b-versatile", "department": Department.COMMUNITY},
    "VOICE": {"provider": "groq", "model": "llama-3.3-70b-versatile", "department": Department.COMMUNITY},

    # INTELLIGENCE (5 agents) - Deepseek R1 Reasoner
    "ORACLE": {"provider": "deepseek", "model": "deepseek-reasoner", "department": Department.INTELLIGENCE},
    "TREND": {"provider": "deepseek", "model": "deepseek-reasoner", "department": Department.INTELLIGENCE},
    "SIGNAL": {"provider": "deepseek", "model": "deepseek-reasoner", "department": Department.INTELLIGENCE},
    "MAP": {"provider": "deepseek", "model": "deepseek-reasoner", "department": Department.INTELLIGENCE},
    "LENS": {"provider": "deepseek", "model": "deepseek-reasoner", "department": Department.INTELLIGENCE},

    # PEOPLE (5 agents) - GPT-4o-mini
    "SOPHIA": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.PEOPLE},
    "HIRE": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.PEOPLE},
    "TRAIN": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.PEOPLE},
    "CULTURE": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.PEOPLE},
    "COMPASS": {"provider": "openai", "model": "gpt-4o-mini", "department": Department.PEOPLE},

    # SECURITY (13 agents) - GPT-4o
    "SENTINEL": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "VAULT": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "PULSE_MON": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "GUARD": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "WATCH": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "LOCK": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "TRACE": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "AUDIT": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "SHIELD_SEC": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "CIPHER": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "PERIMETER": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "RESPONSE": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
    "SCAN": {"provider": "openai", "model": "gpt-4o", "department": Department.SECURITY},
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
