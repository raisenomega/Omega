"""Models and utilities for NOVA chat handler"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_docs: List[Dict[str, Any]] = []


def extract_active_client(messages: List[Dict[str, Any]]) -> Optional[str]:
    """
    Extract active client name from conversation history.
    Detects: "hoy trabajamos [nombre]", "trabajamos con [nombre]",
             "activa [nombre]", "cliente activo: [nombre]"
    """
    pattern = r"(?:hoy trabajamos|trabajamos con|activa|cliente activo[:\s]+)\s*(.+)"
    for msg in reversed(messages):
        if msg.get("role") == "user":
            match = re.search(pattern, msg.get("content", ""), re.IGNORECASE)
            if match:
                client_name = match.group(1).strip()
                return re.sub(r'[.!?,;]$', '', client_name)
    return None
