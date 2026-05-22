"""Personas — system prompts de agentes específicos del Content Lab.

Cada archivo expone {AGENT}_SYSTEM_PROMPT (Final[str]) + {AGENT}_VERSION.
Aplicar como system block en Anthropic API con
cache_control={"type": "ephemeral"} (regla I3 · cache obligatorio).
"""
