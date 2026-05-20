"""Use case: ARIA conversational message generation.

DDD A1 + A9: presentation → application → domain.
§12 ARIA REGLA #2 + §4.1: persistencia OBLIGATORIA en TODOS los paths
(happy · Claude fail · reseller). FIX 4 audit: cada INSERT via
repo.safe_insert · errores logueados pero NUNCA propagan al cliente.
"""
from typing import Optional, Tuple
from app.bc_cognition.domain.persona_aria import (
    build_system_prompt, get_agent_code_for_level, get_history_window,
)
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.infrastructure import aria_repository as repo
from app.bc_cognition.infrastructure._anthropic_types import ClaudeError
from app.infrastructure.supabase_service import get_supabase_service


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
    if r:
        return "reseller", None, r["id"], 3
    return None, None, None, 0


async def use_aria_message(
    user_id: str, user_message: str,
) -> tuple[Optional[ARIAResult], Optional[ClaudeError]]:
    supabase = get_supabase_service()
    role, client_id, reseller_id, level = _resolve_role(supabase, user_id)
    if not role:
        return None, ClaudeError("forbidden", "User no es cliente ni reseller")

    # Pre-Claude · user message + behavioral signal (safe · log si falla)
    repo.safe_insert("user_message", repo.insert_user_message,
                     supabase, user_id, client_id, user_message, level)
    event_id = repo.safe_insert("behavioral_sent", repo.insert_behavioral_event,
                                 supabase, user_id, client_id, reseller_id, "aria_message_sent")

    # Call Claude
    system = build_system_prompt(level, role)
    history = repo.load_recent_history(supabase, user_id, get_history_window(level))
    response, err = await generate(
        agent_code=get_agent_code_for_level(level), system=system,
        messages=history + [{"role": "user", "content": user_message}], max_tokens=1024,
    )

    # Failure path · failure signal + agent_memory was_correct=False
    if err or not response:
        code = err.code if err else "unknown"
        repo.safe_insert("behavioral_failed", repo.insert_behavioral_event,
                         supabase, user_id, client_id, reseller_id,
                         "aria_message_failed", {"error_code": code})
        repo.safe_insert("agent_memory_failed", repo.insert_agent_memory,
                         supabase, user_id, client_id, reseller_id,
                         user_message=user_message, assistant_response=f"[failed:{code}]",
                         level=level, source_event_id=event_id, was_correct=False)
        return None, err or ClaudeError("unknown", "ARIA generate returned None")

    # Happy path · assistant message + agent_memory was_correct=None (cron 72h)
    repo.safe_insert("assistant_message", repo.insert_assistant_message,
                     supabase, user_id, client_id, response.text, level)
    repo.safe_insert("agent_memory_ok", repo.insert_agent_memory,
                     supabase, user_id, client_id, reseller_id,
                     user_message=user_message, assistant_response=response.text,
                     level=level, source_event_id=event_id, was_correct=None)
    return ARIAResult(content=response.text, aria_level=level), None
