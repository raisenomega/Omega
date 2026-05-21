"""Repository clients_v3 · única capa de WRITES Supabase (DDD A1/A9)."""
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    """Best-effort wrapper (audit FIX 4 pattern) · errores loguean stack y NO propagan."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"clients_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def upsert_client(user_id: str, reseller_id: str, identity: dict[str, str]) -> str:
    existing = _sb().table("clients").select("id").eq("user_id", user_id).limit(1).execute()
    if existing.data:
        _sb().table("clients").update(identity).eq("id", existing.data[0]["id"]).execute()
        return str(existing.data[0]["id"])
    r = _sb().table("clients").insert({**identity, "user_id": user_id, "reseller_id": reseller_id}).execute()
    return str(r.data[0]["id"])


def upsert_client_context(client_id: str, context: dict[str, Any]) -> None:
    _sb().table("client_context").upsert({**context, "client_id": client_id}, on_conflict="client_id").execute()


def bulk_insert_social_accounts(client_id: str, accounts: list[dict[str, Any]]) -> None:
    if not accounts: return
    _sb().table("social_accounts").insert([{**a, "client_id": client_id} for a in accounts]).execute()


def upsert_brand_assets(client_id: str, assets: dict[str, Any]) -> None:
    _sb().table("client_brand_assets").upsert({**assets, "client_id": client_id}, on_conflict="client_id").execute()


def insert_brand_voice_samples(client_id: str, samples: list[str]) -> None:
    rows = [{"client_id": client_id, "text": s, "source": "manual_upload", "tone_tags": []} for s in samples if s.strip()]
    if rows:
        _sb().table("brand_voice_corpus").insert(rows).execute()


def insert_behavioral_event(user_id: str, client_id: str, event_type: str, event_data: dict) -> None:
    _sb().table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id, "event_type": event_type, "event_data": event_data,
    }).execute()


def insert_agent_memory(user_id: str, client_id: str, context: str, decision: str, confidence: int) -> None:
    _sb().table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id, "agent_code": "nova", "memory_type": "semantic",
        "context": context, "decision": decision, "confidence": confidence, "was_correct": True,
    }).execute()


def resolve_reseller_for_user(user_id: str) -> Optional[str]:
    r = _sb().table("clients").select("reseller_id").eq("user_id", user_id).limit(1).execute()
    return str(r.data[0]["reseller_id"]) if r.data else None


def update_client_by_id(client_id: str, fields: dict[str, Any]) -> None:
    _sb().table("clients").update(fields).eq("id", client_id).execute()


def delete_social_accounts(client_id: str) -> None:
    _sb().table("social_accounts").delete().eq("client_id", client_id).execute()
