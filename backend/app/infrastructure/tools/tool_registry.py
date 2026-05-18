# backend/app/infrastructure/tools/tool_registry.py
# MAX 200 LINES — R-LINES-001
# Tool Registry — registro central de herramientas disponibles por agente
# R-TOOLS-001: cada agente accede SOLO a sus tools declarados

from app.infrastructure.tools.tool_definitions import (
    TOOL_DEFINITIONS,
    READ_ALLOWED_TABLES,
    WRITE_ALLOWED_TABLES,
)

# ── PERMISOS POR AGENTE ──────────────────────────────────────────────────────
AGENT_TOOL_PERMISSIONS: dict[str, list[str]] = {
    "NOVA":        ["supabase_read", "notification_send", "web_search"],
    "ATLAS":       ["web_search", "fetch_url", "supabase_read", "calendar_write"],
    "LUNA":        ["web_search", "fetch_url", "supabase_read", "supabase_write"],
    "REX":         ["supabase_read", "supabase_write", "calendar_write"],
    "VERA":        ["supabase_read", "supabase_write", "web_search"],
    "KIRA":        ["web_search", "fetch_url", "supabase_read"],
    "ORACLE":      ["web_search", "supabase_read", "supabase_write"],
    "SOPHIA":      ["supabase_read", "supabase_write", "notification_send"],
    "SENTINEL":    ["supabase_read", "web_search", "notification_send"],
    # Marketing agents
    "ATLAS_SUB":   ["web_search", "fetch_url", "supabase_read"],
    "DUDA":        ["supabase_read", "supabase_write"],
    "RAFA":        ["supabase_read", "supabase_write"],
    "MAYA":        ["supabase_read", "supabase_write"],
    "SCOUT":       ["web_search", "fetch_url"],
    "LOLA":        ["web_search", "fetch_url", "supabase_read"],
    "DANI":        ["web_search", "fetch_url"],
    # Security agents
    "VAULT":       ["supabase_read"],
    "DB_GUARDIAN": ["supabase_read"],
    "PULSE_MON":   ["supabase_read", "web_search"],
    # Default fallback
    "DEFAULT":     ["supabase_read"],
}


class ToolRegistry:
    """Registro central de tools. Valida permisos antes de retornar definiciones."""

    @staticmethod
    def get_tools_for_agent(agent_code: str) -> list[dict]:
        """Retorna tool definitions de Claude para un agente específico."""
        allowed = AGENT_TOOL_PERMISSIONS.get(
            agent_code,
            AGENT_TOOL_PERMISSIONS["DEFAULT"]
        )
        return [
            TOOL_DEFINITIONS[tool_name]
            for tool_name in allowed
            if tool_name in TOOL_DEFINITIONS
        ]

    @staticmethod
    def is_tool_allowed(agent_code: str, tool_name: str) -> bool:
        """Verifica si un agente puede usar un tool específico."""
        allowed = AGENT_TOOL_PERMISSIONS.get(
            agent_code,
            AGENT_TOOL_PERMISSIONS["DEFAULT"]
        )
        return tool_name in allowed

    @staticmethod
    def is_table_readable(table: str) -> bool:
        return table in READ_ALLOWED_TABLES

    @staticmethod
    def is_table_writable(table: str) -> bool:
        return table in WRITE_ALLOWED_TABLES
