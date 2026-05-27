"""Use case: ARIA conversational message generation.

DDD A1 + A9: presentation → application → domain.
§12 ARIA REGLA #2 + §4.1: persistencia OBLIGATORIA en TODOS los paths
(happy · Claude fail · reseller). FIX 4 audit: cada INSERT via
repo.safe_insert · errores logueados pero NUNCA propagan al cliente.
"""
from typing import Optional, Tuple
from app.bc_cognition.application._aria_memory_context import load_and_format_memory
from app.bc_cognition.application.web_context import fetch_web_context
from app.bc_cognition.domain.persona_aria import build_system_prompt, get_agent_code_for_level, get_history_window
from app.bc_cognition.domain.client_context_block import build_client_context_block
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.infrastructure import aria_repository as repo, aria_memory_repository as mem
from app.bc_cognition.infrastructure._anthropic_types import ClaudeError
from app.bc_cognition.application._aria_multimodal import build_user_content
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction
from app.infrastructure.supabase_service import get_supabase_service

_UNSAFE = (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW)
_SAFE_REFUSAL = "No puedo procesar ese mensaje por seguridad. ¿En qué más puedo ayudarte con tu contenido o estrategia?"


class ARIAResult:
    def __init__(self, content: str, aria_level: int) -> None:
        self.content = content
        self.aria_level = aria_level


def _resolve_role(supabase, user_id: str) -> Tuple[Optional[str], Optional[str], Optional[str], int]:
    """Retorna (role, client_id, reseller_id, level) · None role si forbidden."""
    c = repo.find_client_by_user(supabase, user_id)
    if c:
        return "client", c["id"], None, c.get("aria_level") or 1
    r = repo.find_reseller_by_owner(supabase, user_id)
    if r:  # DEBT-046: aria_level real (3 base · 4 si aria_premium_reseller)
        return "reseller", None, r["id"], r.get("aria_level") or 3
    return None, None, None, 0


async def use_aria_message(
    user_id: str, user_message: str,
) -> tuple[Optional[ARIAResult], Optional[ClaudeError]]:
    supabase = get_supabase_service()
    role, client_id, reseller_id, level = _resolve_role(supabase, user_id)
    if not role:
        return None, ClaudeError("forbidden", "User no es cliente ni reseller")

    # SPRINT 4A-3 #4: sanear input del cliente (T1/T3/T4 · ARIA_CHAT) antes de store/Claude
    sanitized, serr = sanitize_input(user_message, InputContext.ARIA_CHAT)
    if serr is not None or sanitized is None or sanitized.action in _UNSAFE:
        flags = "" if sanitized is None else ",".join(f.value for f in sanitized.flags)
        await repo.safe_insert("aria_blocked", repo.insert_behavioral_event,
                         supabase, user_id, client_id, reseller_id,
                         "aria_message_blocked", {"flags": flags})
        return ARIAResult(content=_SAFE_REFUSAL, aria_level=level), None
    user_message = sanitized.clean_text  # clean_text en TODOS los stores (decisión A · cero PII cruda)

    # Pre-Claude · user message + behavioral signal (safe · log si falla)
    await repo.safe_insert("user_message", repo.insert_user_message,
                     supabase, user_id, client_id, user_message, level)
    event_id = await repo.safe_insert("behavioral_sent", repo.insert_behavioral_event,
                                 supabase, user_id, client_id, reseller_id, "aria_message_sent")

    # Call Claude · system = persona + contexto cliente (BUG 2) + web actual (auto-search) + memoria (P5)
    base = build_system_prompt(level, role)
    ctx = repo.fetch_aria_context(supabase, client_id) if client_id else None  # context+social+perfil
    ctx_block = build_client_context_block(ctx) if ctx else ""
    vertical = (ctx.get("vertical") or ctx.get("niche") or "") if ctx else ""
    web_block = await fetch_web_context(user_message, vertical, "aria", client_id)
    memory_block = load_and_format_memory(supabase, client_id, reseller_id, query=user_message)
    system = "\n\n".join(p for p in (base, ctx_block, web_block, memory_block) if p)
    history = repo.load_recent_history(supabase, user_id, get_history_window(level))
    user_content = await build_user_content(user_message, ctx.get("_logo_url") if ctx else None)
    response, err = await generate(
        agent_code=get_agent_code_for_level(level), system=system,
        messages=history + [{"role": "user", "content": user_content}], max_tokens=1024,
    )

    # Failure path · failure signal + agent_memory was_correct=False
    if err or not response:
        code = err.code if err else "unknown"
        await repo.safe_insert("behavioral_failed", repo.insert_behavioral_event,
                         supabase, user_id, client_id, reseller_id,
                         "aria_message_failed", {"error_code": code})
        await repo.safe_insert("agent_memory_failed", mem.insert_agent_memory,
                         supabase, user_id, client_id, reseller_id,
                         user_message=user_message, assistant_response=f"[failed:{code}]",
                         level=level, source_event_id=event_id, was_correct=False)
        return None, err or ClaudeError("unknown", "ARIA generate returned None")

    # Happy path · assistant message + agent_memory was_correct=None (cron 72h)
    await repo.safe_insert("assistant_message", repo.insert_assistant_message,
                     supabase, user_id, client_id, response.text, level)
    await repo.safe_insert("agent_memory_ok", mem.insert_agent_memory,
                     supabase, user_id, client_id, reseller_id,
                     user_message=user_message, assistant_response=response.text,
                     level=level, source_event_id=event_id, was_correct=None)
    return ARIAResult(content=response.text, aria_level=level), None
