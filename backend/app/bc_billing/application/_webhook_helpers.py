"""Helpers stateless del webhook dispatcher. Privado · split de _webhook_handlers (C4)."""
from datetime import datetime, timezone
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService


def _lookup_client_by_customer(supabase: SupabaseService, customer_id: Optional[str]) -> Optional[dict]:
    if not customer_id:
        return None
    r = supabase.client.table("clients").select("id").eq("stripe_customer_id", customer_id).execute()
    return r.data[0] if r.data else None


def _iso_from_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
