"""B-2 · persistencia HARDENED del binding Zernio · COMPARTIDA por zernio-sync y el callback headless.
Defensa anti-cross-publish (cierra el incidente 8-jun en el momento de conectar):
  · lee SOLO el profile del negocio (list_accounts(profileId)).
  · re-valida que la cuenta pertenece a ESE profile (no confía solo en el filtro de Zernio).
  · handle AUTORITATIVO de Zernio (username/displayName) · jamás de un input del frontend/redirect.
  · si la cuenta no cayó en el profile correcto → 422, NO guarda (regla cero-mocks).

FIX DE RAÍZ (Fase B · DEBT-ANALYTICS-RESOLVER-PROFILEID): `derive_bindings_from_profile` deriva TODOS los
bindings per-cuenta DESDE el profileId (la llave que siempre funciona) → un negocio nuevo NO puede nacer con
binding vacío. UNA función, dos usos: onboarding (callback) + backfill (negocios viejos). El upsert per-cuenta
está extraído en `_upsert_binding` (idempotente · reusado por persist_zernio_account y por la rutina)."""
from typing import Any, Dict, List, Optional
from fastapi import HTTPException

from app.bc_cognition.infrastructure.zernio_adapter import list_accounts
from app.infrastructure.supabase_service import get_supabase_service


def _profile_of(account: dict) -> Optional[str]:
    """profileId del account · Zernio lo devuelve como objeto {_id, name} (o id plano)."""
    p = account.get("profileId")
    if isinstance(p, dict):
        return str(p.get("_id")) if p.get("_id") else None
    return str(p) if p else None


def _upsert_binding(client_id: str, account: Dict[str, Any]) -> dict:
    """Upsert IDEMPOTENTE de UNA cuenta Zernio → social_accounts(client_id, platform) = zernio_account_id +
    handle autoritativo de Zernio. Update si ya existe (client_id, platform), insert si no → correr 2x deja
    las MISMAS filas (cero duplicados). Extraído del cuerpo de persist_zernio_account (sin cambio de lógica)."""
    sb = get_supabase_service().client
    platform = str(account.get("platform") or "")
    aid = str(account.get("_id"))
    handle = account.get("username") or account.get("displayName")   # autoritativo de Zernio (ignora inputs)
    existing = (sb.table("social_accounts").select("id")
                .eq("client_id", client_id).eq("platform", platform).limit(1).execute().data)
    payload = {"zernio_account_id": aid, "zernio_account_handle": handle,
               "oauth_status": "connected", "status": "active"}
    if existing:
        sb.table("social_accounts").update(payload).eq("id", existing[0]["id"]).execute()
    else:
        sb.table("social_accounts").insert({**payload, "client_id": client_id,
                                            "platform": platform, "account_name": handle or aid}).execute()
    return {"zernio_account_id": aid, "handle": handle, "platform": platform}


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
    return _upsert_binding(client_id, match)


async def derive_bindings_from_profile(client_id: str, profile_id: str) -> List[dict]:
    """LA rutina raíz (onboarding + backfill · MISMA función). list_accounts(profile_id) → por CADA cuenta
    que pertenece al profile, _upsert_binding. Idempotente. Tras conectar, un negocio queda con TODOS sus
    bindings → no puede nacer con binding vacío. AISLAMIENTO: solo cuentas con _profile_of == profile_id."""
    accounts = await list_accounts(profile_id)
    return [_upsert_binding(client_id, a) for a in accounts
            if _profile_of(a) == profile_id and a.get("_id") and a.get("platform")]
