"""Use case: behavioral event tracking · fire-and-forget.

DDD A1 + A9: delegación a aria_repository. Errors swallowed dentro del
use case · jamás propagan al handler (fire-and-forget per spec §4.3).
"""
import logging
from typing import Optional
from app.bc_cognition.infrastructure import aria_repository as repo
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def use_aria_track(
    user_id: str,
    event_type: str,
    event_data: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> None:
    """Persiste behavioral_event si user tiene client_id · silent fail si no."""
    try:
        supabase = get_supabase_service()
        client = repo.find_client_by_user(supabase, user_id)
        if not client:
            return
        # session_id se persiste vía event_data si viene (cols simples · no nueva col)
        data = event_data or {}
        if session_id:
            data["session_id"] = session_id
        repo.insert_behavioral_event(supabase, user_id, client["id"], event_type, data or None)
    except Exception as e:
        logger.warning(f"use_aria_track silent fail: {e}")
