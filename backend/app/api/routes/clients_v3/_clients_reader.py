"""Repository reads · clients_v3 · DDD A1/A9 read-only counterpart of _clients_repository."""
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service


def _sb():
    return get_supabase_service().client


def get_client(client_id: str) -> Optional[dict[str, Any]]:
    r = _sb().table("clients").select("*").eq("id", client_id).limit(1).execute()
    return r.data[0] if r.data else None


def get_client_context(client_id: str) -> dict[str, Any]:
    r = _sb().table("client_context").select("*").eq("client_id", client_id).limit(1).execute()
    return r.data[0] if r.data else {}


def get_social_accounts(client_id: str) -> list[dict[str, Any]]:
    r = _sb().table("social_accounts").select("*").eq("client_id", client_id).order("created_at", desc=False).execute()
    return r.data or []


def get_zernio_account_id(client_id: str, platform: str) -> Optional[str]:
    """F5/2b · mapeo persistido (client_id, platform) → zernio_account_id. None si sin mapeo."""
    r = (_sb().table("social_accounts").select("zernio_account_id")
         .eq("client_id", client_id).eq("platform", platform)
         .not_.is_("zernio_account_id", "null").limit(1).execute())
    return r.data[0]["zernio_account_id"] if r.data else None


def get_brand_assets(client_id: str) -> dict[str, Any]:
    r = _sb().table("client_brand_assets").select("*").eq("client_id", client_id).limit(1).execute()
    return r.data[0] if r.data else {}


def get_brand_voice_samples_manual(client_id: str) -> list[str]:
    r = _sb().table("brand_voice_corpus").select("text").eq("client_id", client_id).eq("source", "manual_upload").order("created_at", desc=False).execute()
    return [x["text"] for x in (r.data or []) if x.get("text")]


def get_user_reseller_ids(user_id: str) -> list[str]:
    r = _sb().table("resellers").select("id").eq("owner_user_id", user_id).execute()
    return [str(x["id"]) for x in (r.data or [])]
