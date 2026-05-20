"""Use case: behavioral event tracking · fire-and-forget.

DDD A1 + A9: delegación a aria_repository. Errors swallowed dentro del
use case · jamás propagan al handler (fire-and-forget per spec §4.3).
Soporta cliente Y reseller (FIX 3 audit · chk_behavioral_owner_present).
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
    """Persiste behavioral_event · cliente o reseller · silent fail."""
    try:
        supabase = get_supabase_service()
        client = repo.find_client_by_user(supabase, user_id)
        client_id = client["id"] if client else None
        reseller_id: Optional[str] = None
        if not client_id:
            reseller = repo.find_reseller_by_owner(supabase, user_id)
            reseller_id = reseller["id"] if reseller else None
        if not client_id and not reseller_id:
            return
        repo.insert_behavioral_event(
            supabase, user_id, client_id, reseller_id,
            event_type, event_data, session_id,
        )
    except Exception as e:
        logger.warning(f"use_aria_track silent fail: {e}")
