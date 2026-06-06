"""
Context Builder - Builds system prompts and agent context for NOVA.
DDD: Application layer helper. Max 200L strict.
"""
from typing import Optional
from datetime import datetime
import logging

from app.services.context_service import ContextService
from app.services.agent_memory_service import AgentMemoryService
from app.infrastructure.supabase_service import get_supabase_service
# Fuente ÚNICA de la persona de NOVA (canónica · 8 agentes + SOPHIA + GUARDIAN).
# El runtime DEBE leer la persona protegida, no un string local divergente.
from app.bc_cognition.domain.persona_nova import NOVA_SYSTEM_PROMPT
from app.bc_cognition.domain.canonical_agents import CANONICAL_AGENTS
from app.bc_cognition.application.nova_aria_learning import aria_learning_for_client

logger = logging.getLogger(__name__)

# Cache for agents context (refresh every 24h)
_agents_cache: Optional[str] = None
_agents_cache_time: Optional[datetime] = None
CACHE_TTL_HOURS = 24

# [R-BUILD-001 equivalent] Anthropic API limit protection
MAX_CONTEXT_CHARS = 60_000
_ARIA_BLOCK_MAX = 3000  # eslabón 3 · cota del bloque "Aprendizaje de ARIA" (~5-8 interacciones)


def _format_aria_learning_block(learning: dict) -> str:
    """Bloque 'APRENDIZAJE DE ARIA (este negocio)' · conteos HONESTOS, cero accuracy %. '' si vacío."""
    interactions = learning.get("interactions") or []
    if not interactions:
        return ""
    c = learning.get("counts") or {}
    lines = [
        "\n\nAPRENDIZAJE DE ARIA (este negocio · lo que ARIA conversó · sin suposiciones):",
        f"{c.get('total', 0)} interacciones · {c.get('with_real_verdict', 0)} con veredicto real · "
        f"{c.get('no_signal', 0)} sin señal de calidad aún.",
    ]
    for it in interactions:
        ctx = (it.get("context_snippet") or "").strip()
        dec = (it.get("decision_snippet") or "").strip()
        if ctx or dec:
            lines.append(f"  • Cliente: {ctx} → ARIA: {dec}")
    return "\n".join(lines)[:_ARIA_BLOCK_MAX]


async def get_agents_context() -> str:
    """Roster canónico de NOVA (8 operativos + SOPHIA + GUARDIAN) · cache 24h.
    Fuente única: CANONICAL_AGENTS (data en memoria · no una tabla de DB muerta)."""
    global _agents_cache, _agents_cache_time
    now = datetime.utcnow()
    if _agents_cache and _agents_cache_time:
        if (now - _agents_cache_time).total_seconds() / 3600 < CACHE_TTL_HOURS:
            return _agents_cache
    lines = [
        "\n\nAGENTES DEL SISTEMA OMEGA (arquitectura canónica · 8 operativos + SOPHIA + GUARDIAN):",
        "\nOPERATIVOS:",
    ]
    for code, a in CANONICAL_AGENTS.items():
        if a["status"] == "operational":
            lines.append(f"  • {code} ({a['name']}): {a['role']}")
    for a in CANONICAL_AGENTS.values():
        if a["status"] == "latent":
            lines.append(f"{a['name']} (meta-agente latente · no corre todavía · se activa con evidencia)")
        elif a["status"] == "subsystem":
            lines.append(f"{a['name']} (sub-sistema de seguridad de comportamiento)")
    lines.append("ARIA es la cara pública (proyección de NOVA hacia clientes/resellers · NO agente adicional).")
    ctx = "\n".join(lines)
    _agents_cache = ctx
    _agents_cache_time = now
    return ctx


async def get_client_context(client_name: str) -> tuple[str, str, str]:
    """
    Get client context from database by name.
    Returns: Tuple of (actual_client_name, client_id, context_text)
    """
    try:
        supabase = get_supabase_service()
        client_resp = supabase.client.table("clients")\
            .select("id, name")\
            .ilike("name", f"%{client_name}%")\
            .limit(1)\
            .execute()
        if not client_resp.data:
            return ("", "", "")
        client = client_resp.data[0]
        client_id = client["id"]
        actual_name = client["name"]
        context_resp = supabase.client.table("context_library")\
            .select("content")\
            .eq("scope", "client")\
            .eq("scope_id", client_id)\
            .eq("is_active", True)\
            .execute()
        if not context_resp.data:
            return (actual_name, client_id, "")
        context_text = "\n\n".join([doc["content"] for doc in context_resp.data])
        return (actual_name, client_id, context_text)
    except Exception as e:
        logger.error(f"Failed to get client context for '{client_name}': {e}")
        return ("", "", "")


async def build_nova_system_prompt(
    context_text: str,
    mentioned_agents: list,
    active_client: str = "",
    client_id: Optional[str] = None,
) -> str:
    """
    Build enhanced system prompt for NOVA with full context.
    Enforces MAX_CONTEXT_CHARS to prevent Anthropic API 400 errors.
    Priority: NOVA base > agents > global (truncated) > client > memory
    """
    context_service = ContextService()
    memory_service = AgentMemoryService()

    agents_context = await get_agents_context()
    global_context = await context_service.get_global_context()

    client_context_text = ""
    if active_client:
        # ctx_client_id NO debe pisar el parámetro client_id (eslabón 3 · bug Commit 3): el explícito
        # de 2.0 tiene que sobrevivir a este bloque para que el bloque ARIA se inyecte en el chat real.
        actual_name, ctx_client_id, client_ctx = await get_client_context(active_client)
        if client_ctx:
            client_context_text = f"\n\nCLIENTE ACTIVO: {actual_name}\nCLIENT_ID: {ctx_client_id}\n{client_ctx}"

    agent_memory_context = ""
    if mentioned_agents:
        agent_context = await memory_service.get_agent_context(mentioned_agents[0])
        if agent_context:
            agent_memory_context = f"\n\nMEMORIA RECIENTE DE {mentioned_agents[0]}:\n{agent_context}"

    # Truncate global_context to prevent 400 — priority kept for base + agents + client
    reserved = len(NOVA_SYSTEM_PROMPT) + len(agents_context) + len(client_context_text) + len(agent_memory_context)
    available = MAX_CONTEXT_CHARS - reserved
    if available > 0 and len(global_context) > available:
        global_context = global_context[:available]
        logger.warning(f"global_context truncated to {available} chars to stay under {MAX_CONTEXT_CHARS}")

    enhanced_system = (
        NOVA_SYSTEM_PROMPT +
        agents_context +
        global_context +
        context_text +
        client_context_text +
        agent_memory_context
    )

    # Eslabón 3 · APRENDIZAJE DE ARIA (este negocio) · prioridad MÁS BAJA: se SUMA al final y se
    # trunca PRIMERO si no entra (persona + roster + global + cliente nunca se tocan). Cero suposiciones.
    if client_id:
        aria_block = _format_aria_learning_block(
            aria_learning_for_client(get_supabase_service(), client_id, limit=8)
        )
        room = MAX_CONTEXT_CHARS - len(enhanced_system)
        if aria_block and room > 0:
            enhanced_system += aria_block[:room]

    return enhanced_system
