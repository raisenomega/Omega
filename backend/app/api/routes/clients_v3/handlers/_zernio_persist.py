"""B-2 · persistencia HARDENED del binding Zernio · COMPARTIDA por zernio-sync y el callback headless.
Defensa anti-cross-publish (cierra el incidente 8-jun en el momento de conectar):
  · lee SOLO el profile del negocio (list_accounts(profileId)).
  · re-valida que la cuenta pertenece a ESE profile (no confía solo en el filtro de Zernio).
  · handle AUTORITATIVO de Zernio (username/displayName) · jamás de un input del frontend/redirect.
  · si la cuenta no cayó en el profile correcto → 422, NO guarda (regla cero-mocks)."""
from typing import Optional
from fastapi import HTTPException

from app.bc_cognition.infrastructure.zernio_adapter import list_accounts
from app.infrastructure.supabase_service import get_supabase_service


def _profile_of(account: dict) -> Optional[str]:
    """profileId del account · Zernio lo devuelve como objeto {_id, name} (o id plano)."""
    p = account.get("profileId")
    if isinstance(p, dict):
        return str(p.get("_id")) if p.get("_id") else None
    return str(p) if p else None


async def persist_zernio_account(client_id: str, platform: str, profile_id: str,
                                 account_id: Optional[str] = None) -> dict:
    """Guarda (client_id, platform) → zernio_account_id+handle SOLO si la cuenta está en el profile del
    negocio. account_id dado (callback headless) → matchea por _id; None (sync manual) → primer match del
    platform. 422 'zernio_account_not_in_profile' si no cuadra (no guarda). Upsert por (client_id, platform)."""
    accounts = await list_accounts(profile_id)
    match = next((a for a in accounts
                  if a.get("platform") == platform and _profile_of(a) == profile_id and a.get("_id")
                  and (account_id is None or str(a.get("_id")) == account_id)), None)
    if not match:
        raise HTTPException(status_code=422, detail="zernio_account_not_in_profile")
    aid = str(match.get("_id"))
    handle = match.get("username") or match.get("displayName")   # autoritativo de Zernio (ignora inputs)
    sb = get_supabase_service().client
    existing = (sb.table("social_accounts").select("id")
                .eq("client_id", client_id).eq("platform", platform).limit(1).execute().data)
    payload = {"zernio_account_id": aid, "zernio_account_handle": handle,
               "oauth_status": "connected", "status": "active"}
    if existing:
        sb.table("social_accounts").update(payload).eq("id", existing[0]["id"]).execute()
    else:
        sb.table("social_accounts").insert({**payload, "client_id": client_id,
                                            "platform": platform, "account_name": handle or aid}).execute()
    return {"zernio_account_id": aid, "handle": handle}
