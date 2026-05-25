"""Repository writes · content_v3 · DDD A1/A9 únicos writes Supabase."""
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.domain.input_threats import redact_pii

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    """Best-effort (audit FIX 4 pattern) · errores loguean stack y NO propagan."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"content_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def update_status(content_id: str, value: str) -> None:
    """Update content_lab_generated.status · valores: draft/approved/rejected/scheduled/published."""
    _sb().table("content_lab_generated").update({"status": value}).eq("id", content_id).execute()


def insert_brand_voice_corpus_approved(client_id: str, text: str, platform: Optional[str]) -> None:
    if not text.strip():
        return
    _sb().table("brand_voice_corpus").insert({
        "client_id": client_id, "text": text, "source": "approved_draft",
        "tone_tags": [], "platform": platform,
    }).execute()


def insert_agent_memory_approved(user_id: str, client_id: str, content_text: str) -> None:
    _sb().table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id, "agent_code": "brand_voice",
        "memory_type": "semantic", "context": redact_pii(content_text)[0][:500],
        "decision": "approved_by_client", "confidence": 10, "was_correct": True,
    }).execute()
