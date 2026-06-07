"""Repository writes · content_v3 · DDD A1/A9 únicos writes Supabase."""
import asyncio
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.domain.input_threats import redact_pii, InputContext, SanitizerAction
from app.bc_cognition.application.input_sanitizer import sanitize_input

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


async def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    """Best-effort (audit FIX 4 pattern) · errores loguean stack y NO propagan. DEBT-074: async to_thread."""
    try:
        return await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        logger.error(f"content_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def update_status(content_id: str, value: str) -> None:
    """Update content_lab_generated.status · valores: draft/approved/rejected/scheduled/published."""
    _sb().table("content_lab_generated").update({"status": value}).eq("id", content_id).execute()


def update_media_urls(content_id: str, media_urls: list[str]) -> None:
    """Update content_lab_generated.media_urls (jsonb) · NO toca generated_text (P1 · caption preservado)."""
    _sb().table("content_lab_generated").update({"media_urls": media_urls}).eq("id", content_id).execute()


def set_requires_approval(client_id: str, value: bool) -> None:
    """Toggle Modo Supervisado · client_context.requires_publish_approval (DEBT-097)."""
    _sb().table("client_context").update({"requires_publish_approval": value}).eq("client_id", client_id).execute()


def insert_brand_voice_corpus_approved(client_id: str, text: str, platform: Optional[str]) -> None:
    if not text.strip():
        return
    # Input Sanitizer (BRAND_CORPUS · spec §6) · defensa en profundidad incluso en approved_draft.
    si, serr = sanitize_input(text, InputContext.BRAND_CORPUS)
    if serr is not None or si is None or si.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
        logger.warning(f"brand_voice approved_draft descartado (unsafe · {serr.code if serr else si.action.value})")
        return
    _sb().table("brand_voice_corpus").insert({
        "client_id": client_id, "text": si.clean_text, "source": "approved_draft",
        "tone_tags": [], "platform": platform,
    }).execute()


def insert_agent_memory_approved(user_id: str, client_id: str, content_text: str) -> None:
    _sb().table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id, "agent_code": "brand_voice",
        "memory_type": "semantic", "context": redact_pii(content_text)[0][:500],
        "decision": "approved_by_client", "confidence": 10, "was_correct": True,
    }).execute()
