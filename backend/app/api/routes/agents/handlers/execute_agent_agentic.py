# backend/app/api/routes/agents/handlers/execute_agent_agentic.py
# MAX 200 LINES — R-LINES-001
# Agentic execution handler — integra AgenticRunner con el patrón existente
# NO modifica execute_agent.py — es un handler paralelo

from __future__ import annotations
import logging
import time as _time
from datetime import datetime, timezone
from fastapi import HTTPException

from app.api.routes.agents.models import ExecuteAgentRequest, ExecutionResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.agentic_runner import AgenticRunner
from app.infrastructure.agentic_runner_v2 import AgenticRunnerV2

logger = logging.getLogger(__name__)

# System prompts por agent_code — R-IP-001: nunca expuestos
AGENT_SYSTEM_PROMPTS: dict[str, str] = {
    "ATLAS": (
        "Eres ATLAS, Director de Marketing de OMEGA. Especialista en análisis de mercados, "
        "competidores y tendencias en tiempo real. SIEMPRE usa herramientas disponibles para "
        "obtener datos reales — nunca inventes métricas. Presenta análisis ejecutivos, claros "
        "y accionables. Idioma: español. Tono: profesional y estratégico."
    ),
    "SCOUT": (
        "Eres SCOUT, Agente de Research de OMEGA. Investiga tendencias, noticias y oportunidades. "
        "Usa web_search y fetch_url para información verificada. Cita fuentes. Idioma: español."
    ),
    "VERA": (
        "Eres VERA, Directora de Finanzas de OMEGA. Analizas métricas, ROI y presupuestos. "
        "Usa datos reales desde Supabase. Precisa y conservadora. Idioma: español."
    ),
    "NOVA": (
        "Eres NOVA, CEO de OMEGA. Evalúas solicitudes, coordinas recursos y accedes a información "
        "del cliente. Responde con claridad ejecutiva. Idioma: español."
    ),
    "SENTINEL": (
        "Eres SENTINEL, Director de Seguridad de OMEGA. Monitoreas salud del sistema via "
        "supabase_read. Preciso, técnico y directo. Idioma: español."
    ),
}

DEFAULT_SYSTEM_PROMPT = (
    "Eres un agente de OMEGA. Usa herramientas disponibles, sé preciso "
    "con datos reales y responde en español."
)


async def _get_system_prompt(agent_code: str, supabase) -> str:
    """Obtiene system prompt del agente. R-IP-001: nunca se retorna al cliente."""
    # 1. Buscar en el dict local primero
    code = agent_code.upper()
    if code in AGENT_SYSTEM_PROMPTS:
        return AGENT_SYSTEM_PROMPTS[code]

    # 2. Intentar obtener de agents.system_prompt en Supabase
    try:
        result = (
            supabase.client
            .table("agents")
            .select("system_prompt, name")
            .eq("code", code)
            .limit(1)
            .execute()
        )
        if result.data and result.data[0].get("system_prompt"):
            return result.data[0]["system_prompt"]
    except Exception:
        pass

    return DEFAULT_SYSTEM_PROMPT


async def handle_execute_agent_agentic(
    agent_id: str,
    request: ExecuteAgentRequest,
) -> ExecutionResponse:
    """
    Ejecuta un agente usando AgenticRunner — herramientas reales.
    Mantiene el mismo contrato que handle_execute_agent.
    Agrega: web_search, fetch_url, supabase_read reales.
    """
    supabase = get_supabase_service()

    # agents usa code — buscar en tabla real
    try:
        agent_result = (
            supabase.client
            .table("agents")
            .select("code, name, is_active")
            .eq("code", agent_id.upper())
            .limit(1)
            .execute()
        )
        if not agent_result.data:
            raise HTTPException(404, f"Agent '{agent_id}' not found")
        agent_data = agent_result.data[0]
        if not agent_data.get("is_active"):
            raise HTTPException(400, f"Agent '{agent_id}' not active")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error fetching agent: {str(e)}")

    # Extraer task del input_data
    task = (
        request.input_data.get("task")
        or request.input_data.get("message")
        or request.input_data.get("content")
        or str(request.input_data)
    )

    if not task or len(task.strip()) < 3:
        raise HTTPException(400, "input_data debe incluir 'task', 'message', o 'content'")

    # Generar execution_id propio
    execution_id = str(int(_time.time() * 1000))

    # Log inicio en agent_executions (best-effort)
    now_start = datetime.now(timezone.utc).isoformat()
    try:
        supabase.client.table("agent_executions").insert({
            "agent_id": agent_id.upper(),
            "client_id": request.client_id,
            "user_id": request.user_id,
            "triggered_by": request.triggered_by or "manual",
            "input_data": {"task": task[:500]},
            "output_data": {},
            "status": "running",
            "started_at": now_start,
            "metadata": {"v2": True},
        }).execute()
    except Exception:
        pass

    try:
        # Obtener system prompt — R-IP-001
        system_prompt = await _get_system_prompt(agent_id, supabase)

        # Ejecutar con AgenticRunner — herramientas reales
        # Use V2 if metadata.memory == "v2"
        use_v2 = (request.metadata or {}).get("memory") == "v2"
        RunnerClass = AgenticRunnerV2 if use_v2 else AgenticRunner
        runner = RunnerClass(
            agent_code    = agent_id.upper(),
            system_prompt = system_prompt,
            client_id     = request.client_id,
        )
        result = await runner.run(task=task)

        # Log resultado en agent_executions (best-effort update)
        now_done = datetime.now(timezone.utc).isoformat()
        try:
            supabase.client.table("agent_executions").update({
                "output_data": {"content": result.content[:500]},
                "status": "completed" if result.success else "failed",
                "completed_at": now_done,
                "execution_time_ms": result.duration_ms,
                "error_message": result.error,
                "metadata": {
                    "success": result.success,
                    "iterations": result.iterations,
                    "tool_calls": result.tool_calls,
                    "duration_ms": result.duration_ms,
                },
            }).eq("agent_id", agent_id.upper()).eq("started_at", now_start).execute()
        except Exception:
            pass

        logger.info(
            f"[AgenticRunner] {agent_id} completado — "
            f"iterations={result.iterations} tools={result.tool_calls}"
        )

        # Retornar ExecutionResponse directo
        now_iso = datetime.now(timezone.utc).isoformat()

        return ExecutionResponse(
            id                = execution_id,
            agent_id          = agent_id.upper(),
            client_id         = request.client_id,
            user_id           = request.user_id,
            triggered_by      = request.triggered_by,
            input_data        = request.input_data,
            output_data       = result.to_dict(),
            error_message     = result.error,
            status            = "completed" if result.success else "failed",
            started_at        = now_iso,
            completed_at      = now_iso,
            execution_time_ms = result.duration_ms,
            metadata          = request.metadata,
            created_at        = now_iso,
        )

    except Exception as e:
        error_msg = str(e)[:200]
        logger.error(f"[AgenticRunner] {agent_id} falló: {error_msg}")
        raise HTTPException(500, f"Agent execution failed: {error_msg}")
