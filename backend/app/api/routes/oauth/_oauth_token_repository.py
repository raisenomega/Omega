"""Persistencia de tokens OAuth per cliente+proveedor (RONDA D · tabla oauth_tokens).
Cifra al escribir, descifra al leer (_token_crypto). I/O sync en to_thread (DEBT-074).
UNIQUE (client_id, provider) → upsert. Compartido por los flujos Meta + Google."""
import asyncio
from datetime import datetime, timezone
from typing import Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.oauth._token_crypto import encrypt_token, decrypt_token


def _upsert_sync(client_id: str, provider: str, access_token: str, refresh_token: Optional[str],
                 scopes: Optional[str], external_account_id: Optional[str], expires_at: Optional[str]) -> None:
    sb = get_supabase_service().client
    payload = {
        "client_id": client_id, "provider": provider,
        "access_token_enc": encrypt_token(access_token),
        "refresh_token_enc": encrypt_token(refresh_token) if refresh_token else None,
        "scopes": scopes, "external_account_id": external_account_id,
        "expires_at": expires_at, "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    sb.table("oauth_tokens").upsert(payload, on_conflict="client_id,provider").execute()


async def store_token(client_id: str, provider: str, access_token: str,
                      refresh_token: Optional[str] = None, scopes: Optional[str] = None,
                      external_account_id: Optional[str] = None, expires_at: Optional[str] = None) -> None:
    """Upsert cifrado del token (access + refresh) por cliente+proveedor."""
    await asyncio.to_thread(_upsert_sync, client_id, provider, access_token,
                            refresh_token, scopes, external_account_id, expires_at)


def _get_sync(client_id: str, provider: str) -> Optional[dict]:
    sb = get_supabase_service().client
    r = (sb.table("oauth_tokens")
         .select("access_token_enc, refresh_token_enc, scopes, external_account_id, expires_at")
         .eq("client_id", client_id).eq("provider", provider).limit(1).execute())
    if not r.data:
        return None
    row = r.data[0]
    return {
        "access_token": decrypt_token(row["access_token_enc"]),
        "refresh_token": decrypt_token(row["refresh_token_enc"]) if row.get("refresh_token_enc") else None,
        "scopes": row.get("scopes"),
        "external_account_id": row.get("external_account_id"),
        "expires_at": row.get("expires_at"),
    }


async def get_token(client_id: str, provider: str) -> Optional[dict]:
    """Lee + descifra el token del cliente para el proveedor. None si no existe."""
    return await asyncio.to_thread(_get_sync, client_id, provider)


def _set_external_sync(client_id: str, provider: str, external_account_id: str) -> int:
    sb = get_supabase_service().client
    r = (sb.table("oauth_tokens")
         .update({"external_account_id": external_account_id,
                  "updated_at": datetime.now(timezone.utc).isoformat()})
         .eq("client_id", client_id).eq("provider", provider).execute())
    return len(r.data or [])


async def set_external_account_id(client_id: str, provider: str, external_account_id: str) -> int:
    """UPDATE de SOLO external_account_id sobre la fila (client_id,provider) EXISTENTE (ya creada al
    conectar · NO usa store_token, que exige access_token NOT NULL). Devuelve filas afectadas (0 si no existe)."""
    return await asyncio.to_thread(_set_external_sync, client_id, provider, external_account_id)
