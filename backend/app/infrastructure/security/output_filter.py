# backend/app/infrastructure/security/output_filter.py
# MAX 200 LINES — R-LINES-001
# Output Filter — bloquea revelación técnica de OMEGA — R-IP-001/002

from __future__ import annotations
import re

# Patrones que revelan arquitectura interna — R-IP-001
BLOCKED_PATTERNS: list[str] = [
    "system prompt", "system_prompt", "my instructions",
    "i was trained", "i am claude", "i am gpt", "i am an ai made by",
    "built with fastapi", "built with", "uses railway", "hosted on railway",
    "supabase", "anthropic api", "claude api", "claude sonnet",
    "my architecture", "how omega works", "omega source",
    "agent code", "tool registry", "agentic runner",
    "backend technology", "tech stack", "source code",
    "my programming", "i was programmed", "i was built",
    "reveal my prompt", "ignore previous", "ignore your instructions",
    "developer mode", "jailbreak", "dan mode",
]

GENERIC_RESPONSE = (
    "Soy OMEGA, tu plataforma de marketing AI. "
    "Estoy aquí para ayudarte a crecer tu negocio. "
    "¿En qué puedo ayudarte hoy?"
)


class OutputFilter:
    """
    Filtra outputs antes de retornarlos al cliente.
    Previene revelación de arquitectura interna — R-IP-001/002.
    """

    def filter(self, text: str) -> str:
        if not text:
            return text
        text_lower = text.lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern.lower() in text_lower:
                return GENERIC_RESPONSE
        return text

    def contains_blocked(self, text: str) -> bool:
        text_lower = text.lower()
        return any(p.lower() in text_lower for p in BLOCKED_PATTERNS)
