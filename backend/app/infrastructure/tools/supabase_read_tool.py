# backend/app/infrastructure/tools/supabase_read_tool.py
# MAX 200 LINES — R-LINES-001
# Supabase Read Tool — consultas seguras a DB por agentes
# R-TENANT-001: client_id siempre en WHERE — nunca confiar al agente

from __future__ import annotations
import time
from typing import Any
from app.infrastructure.tools.tool_registry import ToolRegistry
from app.infrastructure.supabase_service import get_supabase_service

# Tablas que NO filtran por client_id — son globales del sistema
GLOBAL_TABLES = {
    "omega_agents",
    "sentinel_scans",
}


async def _log_tool_call(
    agent_code: str,
    client_id: str | None,
    input_summary: str,
    success: bool,
    duration_ms: int
) -> None:
    """Audit log — R-OPS-001"""
    try:
        supabase = get_supabase_service()
        supabase.client.table("omega_tool_calls").insert({
            "id": str(int(time.time() * 1000)),
            "agent_code": agent_code,
            "tool_name": "supabase_read",
            "client_id": client_id,
            "input_summary": input_summary[:200],
            "success": success,
            "duration_ms": duration_ms,
        }).execute()
    except Exception:
        pass


async def supabase_read(
    table: str,
    agent_code: str,
    client_id: str | None = None,
    filters: dict | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Lee datos de Supabase para el agente.
    R-TENANT-001: client_id se inyecta automáticamente en el WHERE.
    R-TOOLS-001: solo tablas en READ_ALLOWED_TABLES son accesibles.
    """
    if not ToolRegistry.is_table_readable(table):
        return {
            "success": False,
            "error": f"Tabla '{table}' no está autorizada para lectura",
            "data": []
        }

    if not client_id and table not in GLOBAL_TABLES:
        return {
            "success": False,
            "error": "client_id requerido para consultar esta tabla",
            "data": []
        }

    limit = min(max(1, limit), 50)  # clamp 1-50
    filters = filters or {}
    start  = time.time()

    try:
        supabase = get_supabase_service()
        query    = supabase.client.table(table).select("*")

        # R-TENANT-001: inyectar client_id automáticamente
        if client_id and table not in GLOBAL_TABLES:
            query = query.eq("client_id", client_id)

        # Aplicar filtros adicionales del agente
        for field, value in filters.items():
            if field == "client_id":
                continue  # ya inyectado arriba — ignorar si el agente lo repite
            query = query.eq(field, value)

        query = query.limit(limit)
        result = query.execute()

        duration_ms = int((time.time() - start) * 1000)
        rows = result.data or []

        await _log_tool_call(
            agent_code, client_id,
            f"table={table} filters={list(filters.keys())} limit={limit}",
            True, duration_ms
        )

        return {
            "success":     True,
            "table":       table,
            "data":        rows,
            "count":       len(rows),
            "duration_ms": duration_ms,
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        await _log_tool_call(
            agent_code, client_id,
            f"table={table}",
            False, duration_ms
        )
        return {
            "success": False,
            "error":   str(e)[:200],
            "data":    []
        }


async def supabase_write(
    table: str,
    data: dict,
    agent_code: str,
    client_id: str | None = None,
    operation: str = "insert",
) -> dict[str, Any]:
    """
    Escribe datos en Supabase.
    R-TENANT-001: client_id se inyecta automáticamente.
    R-TOOLS-001: solo tablas en WRITE_ALLOWED_TABLES son accesibles.
    """
    if not ToolRegistry.is_table_writable(table):
        return {
            "success": False,
            "error": f"Tabla '{table}' no está autorizada para escritura",
        }

    if not client_id:
        return {
            "success": False,
            "error": "client_id requerido para escritura",
        }

    # R-TENANT-001: inyectar client_id — no confiar en el agente
    data["client_id"] = client_id
    if "id" not in data:
        data["id"] = str(int(time.time() * 1000))

    start = time.time()

    try:
        supabase = get_supabase_service()

        if operation == "upsert":
            result = supabase.client.table(table).upsert(data).execute()
        else:
            result = supabase.client.table(table).insert(data).execute()

        duration_ms = int((time.time() - start) * 1000)

        await _log_tool_call(
            agent_code, client_id,
            f"table={table} op={operation}",
            True, duration_ms
        )

        return {
            "success":     True,
            "table":       table,
            "operation":   operation,
            "duration_ms": duration_ms,
        }

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        await _log_tool_call(
            agent_code, client_id,
            f"table={table} op={operation}",
            False, duration_ms
        )
        return {
            "success": False,
            "error":   str(e)[:200],
        }


def format_for_claude(result: dict[str, Any]) -> str:
    """Convierte resultado de supabase_read a texto legible para el agente."""
    if not result.get("success"):
        return f"[supabase_read ERROR]: {result.get('error', 'Error desconocido')}"

    rows = result.get("data", [])
    if not rows:
        return f"[supabase_read] Tabla '{result['table']}': sin resultados"

    import json
    return (
        f"[supabase_read] Tabla '{result['table']}' — {result['count']} registros:\n"
        + json.dumps(rows, ensure_ascii=False, default=str)[:3000]
    )
