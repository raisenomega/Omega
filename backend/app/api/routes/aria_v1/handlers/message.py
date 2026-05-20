"""POST /api/v1/aria/message · genera respuesta ARIA + 4 INSERTs obligatorios.

Spec ARIA_NOVA_INTELLIGENCE.md §4-§5 · regla §12 #2:
TODO mensaje → INSERT agent_memory + behavioral_events sin excepción.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from app.api.routes.aria_v1.models import ARIAMessageRequest, ARIAMessageResponse
from app.api.routes.aria_v1.handlers import _aria_persistence as p
from app.api.routes.auth.auth_utils import get_current_user
from app.bc_cognition.domain.persona_aria import (
    build_system_prompt, get_agent_code_for_level, get_history_window,
)
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ARIAMessageResponse)
async def aria_message(
    request: ARIAMessageRequest,
    authorization: Optional[str] = Header(None),
) -> ARIAMessageResponse:
    user = await get_current_user(authorization)
    user_id = user["id"]
    supabase = get_supabase_service()

    client_row = supabase.client.table("clients").select(
        "id, aria_level"
    ).eq("user_id", user_id).limit(1).execute()
    if client_row.data:
        role, client_id, level = "client", client_row.data[0]["id"], client_row.data[0].get("aria_level") or 1
    else:
        rs = supabase.client.table("resellers").select("id").eq(
            "owner_user_id", user_id
        ).limit(1).execute()
        if not rs.data:
            raise HTTPException(status_code=403, detail="User no es cliente ni reseller")
        role, client_id, level = "reseller", None, 3

    system = build_system_prompt(level, role)
    agent_code = get_agent_code_for_level(level)
    history = p.load_recent_history(supabase, user_id, get_history_window(level))
    messages = history + [{"role": "user", "content": request.content}]

    response, err = await generate(agent_code=agent_code, system=system, messages=messages, max_tokens=1024)
    if err or not response:
        logger.error(f"ARIA generate failed: {err}")
        raise HTTPException(status_code=503, detail="ARIA no disponible temporalmente")

    assistant_text = response.text

    p.insert_user_message(supabase, user_id, client_id, request.content, level)
    p.insert_assistant_message(supabase, user_id, client_id, assistant_text, level)
    if client_id:
        event_id = p.insert_behavioral_event(supabase, user_id, client_id, "aria_message_sent")
        p.insert_agent_memory(
            supabase=supabase,
            user_id=user_id,
            client_id=client_id,
            user_message=request.content,
            assistant_response=assistant_text,
            level=level,
            source_event_id=event_id,
        )

    return ARIAMessageResponse(content=assistant_text, aria_level=level)
