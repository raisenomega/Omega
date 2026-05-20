"""Use case: ARIA conversational message generation.

DDD A1 + A9: presentation → application → domain.
Orquesta: persona_aria (domain) + anthropic_adapter (infra)
+ aria_repository (infra). Result-tuple shape (response, error) ·
nunca lanza al caller.
"""
from typing import Optional
from app.bc_cognition.domain.persona_aria import (
    build_system_prompt, get_agent_code_for_level, get_history_window,
)
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.infrastructure import aria_repository as repo
from app.bc_cognition.infrastructure._anthropic_types import ClaudeError
from app.infrastructure.supabase_service import get_supabase_service


class ARIAResult:
    """Result success shape · análogo a ClaudeResponse."""
    def __init__(self, content: str, aria_level: int) -> None:
        self.content = content
        self.aria_level = aria_level


async def use_aria_message(
    user_id: str, user_message: str,
) -> tuple[Optional[ARIAResult], Optional[ClaudeError]]:
    """Genera respuesta ARIA + persiste 4 INSERTs en happy path.

    FIX 3 ampliará persistencia a todos los paths (Claude fail · reseller).
    """
    supabase = get_supabase_service()

    client = repo.find_client_by_user(supabase, user_id)
    if client:
        role, client_id, level = "client", client["id"], client.get("aria_level") or 1
    else:
        reseller = repo.find_reseller_by_owner(supabase, user_id)
        if not reseller:
            return None, ClaudeError("forbidden", "User no es cliente ni reseller")
        role, client_id, level = "reseller", None, 3

    system = build_system_prompt(level, role)
    agent_code = get_agent_code_for_level(level)
    history = repo.load_recent_history(supabase, user_id, get_history_window(level))
    messages = history + [{"role": "user", "content": user_message}]

    response, err = await generate(
        agent_code=agent_code, system=system, messages=messages, max_tokens=1024,
    )
    if err or not response:
        return None, err or ClaudeError("unknown", "ARIA generate returned None")

    repo.insert_user_message(supabase, user_id, client_id, user_message, level)
    repo.insert_assistant_message(supabase, user_id, client_id, response.text, level)
    if client_id:
        event_id = repo.insert_behavioral_event(supabase, user_id, client_id, "aria_message_sent")
        repo.insert_agent_memory(
            supabase=supabase, user_id=user_id, client_id=client_id,
            user_message=user_message, assistant_response=response.text,
            level=level, source_event_id=event_id,
        )

    return ARIAResult(content=response.text, aria_level=level), None
