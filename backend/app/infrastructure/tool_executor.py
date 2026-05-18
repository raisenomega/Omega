# backend/app/infrastructure/tool_executor.py
# MAX 200 LINES — R-LINES-001
# Tool Executor — ejecuta tools con validación de permisos
# R-TOOLS-001: valida permisos antes de ejecutar

from __future__ import annotations
import json
from typing import Any

from app.infrastructure.tools.tool_registry import ToolRegistry
from app.infrastructure.tools.web_search_tool import web_search, format_for_claude as fmt_search
from app.infrastructure.tools.fetch_url_tool import fetch_url, format_for_claude as fmt_fetch
from app.infrastructure.tools.supabase_read_tool import (
    supabase_read, supabase_write,
    format_for_claude as fmt_supabase
)


class ToolExecutor:
    """
    Ejecuta tool calls con validación de permisos.
    Delegado por AgenticRunner para separar responsabilidades.
    """

    def __init__(self, agent_code: str, client_id: str | None = None):
        self.agent_code = agent_code
        self.client_id  = client_id

    async def execute_tools(
        self,
        content_blocks: list,
        tool_calls_log: list[str],
    ) -> list[dict]:
        """Ejecuta los tool calls validando permisos. R-TOOLS-001."""
        results = []

        for block in content_blocks:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input

            # R-TOOLS-001: validar permiso antes de ejecutar
            if not ToolRegistry.is_tool_allowed(self.agent_code, tool_name):
                results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     f"[BLOCKED] Tool '{tool_name}' no autorizado para {self.agent_code}",
                })
                continue

            tool_calls_log.append(tool_name)
            result_text = await self._call_tool(tool_name, tool_input)

            results.append({
                "type":        "tool_result",
                "tool_use_id": block.id,
                "content":     result_text,
            })

        return results

    async def _call_tool(self, tool_name: str, tool_input: dict) -> str:
        """Despacha la llamada al tool correcto."""
        try:
            if tool_name == "web_search":
                result = await web_search(
                    query       = tool_input.get("query", ""),
                    agent_code  = self.agent_code,
                    client_id   = self.client_id,
                    max_results = tool_input.get("max_results", 3),
                )
                return fmt_search(result)

            if tool_name == "fetch_url":
                result = await fetch_url(
                    url          = tool_input.get("url", ""),
                    agent_code   = self.agent_code,
                    client_id    = self.client_id,
                    extract_type = tool_input.get("extract_type", "text"),
                )
                return fmt_fetch(result)

            if tool_name == "supabase_read":
                result = await supabase_read(
                    table      = tool_input.get("table", ""),
                    agent_code = self.agent_code,
                    client_id  = self.client_id,
                    filters    = tool_input.get("filters", {}),
                    limit      = tool_input.get("limit", 10),
                )
                return fmt_supabase(result)

            if tool_name == "supabase_write":
                result = await supabase_write(
                    table      = tool_input.get("table", ""),
                    data       = tool_input.get("data", {}),
                    agent_code = self.agent_code,
                    client_id  = self.client_id,
                    operation  = tool_input.get("operation", "insert"),
                )
                return json.dumps(result, ensure_ascii=False)

            return f"[Tool '{tool_name}' no implementado aún]"

        except Exception as e:
            return f"[Tool '{tool_name}' ERROR]: {str(e)[:150]}"

    @staticmethod
    def extract_text(content_blocks: list) -> str:
        """Extrae texto de los content blocks de Claude."""
        return " ".join(
            block.text
            for block in content_blocks
            if hasattr(block, "text") and block.text
        ).strip()
