"""
AI Providers Package
Multi-AI provider abstraction layer for OMEGA agents.
Fase 2 §2.6: eliminados los providers legacy no-Anthropic (DDD I1).
Solo Anthropic queda como provider permitido para texto.
"""
from .base_provider import BaseAIProvider, AIProviderResponse, ChatMessage, MessageRole
from .anthropic_provider import AnthropicProvider

__all__ = [
    "BaseAIProvider",
    "AIProviderResponse",
    "ChatMessage",
    "MessageRole",
    "AnthropicProvider"
]
