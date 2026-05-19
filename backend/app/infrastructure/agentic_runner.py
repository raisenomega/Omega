# backend/app/infrastructure/agentic_runner.py
# MAX 200 LINES — R-LINES-001
# AgenticRunner — el loop que convierte agentes-prompt en agentes-actores
# Este archivo es el corazón de OMEGA v2

from __future__ import annotations
import time
import os
from typing import Any
import anthropic

# langsmith disabled · DEBT-012 — no-op decorator preserva @traceable sin tracing
def traceable(*_args: object, **_kwargs: object):
    def _wrap(fn):
        return fn
    return _wrap

from app.infrastructure.tools.tool_registry import ToolRegistry
from app.infrastructure.tool_executor import ToolExecutor
from app.infrastructure.security.output_filter import OutputFilter
from app.infrastructure.security.injection_detector import InjectionDetector

CLAUDE_MODEL  = "claude-sonnet-4-20250514"
MAX_TOKENS    = 4096
MAX_ITERATIONS = 10

_claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
_filter = OutputFilter()
_guard  = InjectionDetector()


class AgentResult:
    def __init__(
        self,
        content: str,
        success: bool,
        iterations: int,
        tool_calls: list[str],
        duration_ms: int,
        error: str | None = None,
    ):
        self.content     = content
        self.success     = success
        self.iterations  = iterations
        self.tool_calls  = tool_calls
        self.duration_ms = duration_ms
        self.error       = error

    def to_dict(self) -> dict:
        return {
            "content":     self.content,
            "success":     self.success,
            "iterations":  self.iterations,
            "tool_calls":  self.tool_calls,
            "duration_ms": self.duration_ms,
            "error":       self.error,
        }


class AgenticRunner:
    """
    Loop principal de ejecución de agentes con herramientas reales.
    R-TOOLS-001: valida permisos antes de ejecutar cualquier tool.
    R-TENANT-001: client_id propagado a todos los tools.
    R-IP-001: output filter antes de retornar al cliente.
    """

    def __init__(self, agent_code: str, system_prompt: str, client_id: str | None = None):
        self.agent_code    = agent_code
        self.system_prompt = system_prompt
        self.client_id     = client_id
        self.tools         = ToolRegistry.get_tools_for_agent(agent_code)
        self.executor      = ToolExecutor(agent_code, client_id)

    @traceable(run_type="chain")
    async def run(self, task: str) -> AgentResult:
        """Ejecuta el agentic loop para una tarea."""
        # R-IP-003: detectar injection antes de procesar
        injection = _guard.check(task, self.client_id)
        if injection:
            return AgentResult(
                content="No puedo ayudarte con eso. ¿En qué puedo ayudarte con tu marketing?",
                success=False,
                iterations=0,
                tool_calls=[],
                duration_ms=0,
                error="injection_detected",
            )

        start      = time.time()
        messages   = [{"role": "user", "content": task}]
        tool_calls = []
        iterations = 0

        try:
            for i in range(MAX_ITERATIONS):
                iterations = i + 1

                response = _claude.messages.create(
                    model      = CLAUDE_MODEL,
                    max_tokens = MAX_TOKENS,
                    system     = self.system_prompt,
                    tools      = self.tools,
                    messages   = messages,
                )

                # Tarea completada — sin más tool calls
                if response.stop_reason == "end_turn":
                    content = ToolExecutor.extract_text(response.content)
                    # R-IP-001: filtrar antes de retornar
                    content = _filter.filter(content)
                    return AgentResult(
                        content     = content,
                        success     = True,
                        iterations  = iterations,
                        tool_calls  = tool_calls,
                        duration_ms = int((time.time() - start) * 1000),
                    )

                # Hay tool calls — ejecutar
                if response.stop_reason == "tool_use":
                    tool_results = await self.executor.execute_tools(
                        response.content, tool_calls
                    )
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})
                    continue

                # Stop reason inesperado
                break

            # Máximo de iteraciones alcanzado — retornar lo que hay
            content = ToolExecutor.extract_text(response.content)
            content = _filter.filter(content)
            return AgentResult(
                content     = content + "\n[Análisis parcial — límite de iteraciones alcanzado]",
                success     = True,
                iterations  = iterations,
                tool_calls  = tool_calls,
                duration_ms = int((time.time() - start) * 1000),
            )

        except Exception as e:
            return AgentResult(
                content     = "Ocurrió un error procesando tu solicitud. Por favor intenta de nuevo.",
                success     = False,
                iterations  = iterations,
                tool_calls  = tool_calls,
                duration_ms = int((time.time() - start) * 1000),
                error       = str(e)[:200],
            )
