"""Dependency require_super_owner · gate Security Dev (más estricto que require_superadmin).

require_superadmin  → is_owner=true  (cualquier dueño de reseller)
require_super_owner → is_super_owner=true (SOLO Ibrain · operador OMEGA)

Defense-in-depth: DB unique index + este gate backend + RLS + frontend condicional.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service


async def is_super_owner_id(user_id: str) -> bool:
    """True si user_id es dueño de un reseller con is_super_owner=true.
    Filtra por is_super_owner=true directo (NO limit(1) sobre owner_user_id solo):
    owner_user_id no es único (00023) y el flag vive en 1 sola fila → un limit(1)
    ciego podría traer una fila no-marcada y dar falso negativo. Robusto a N resellers."""
    sb = get_supabase_service().client
    r = sb.table("resellers").select("id") \
        .eq("owner_user_id", str(user_id)).eq("is_super_owner", True).limit(1).execute()
    return bool(r.data)


async def require_super_owner(authorization: Optional[str]) -> Dict[str, Any]:
    """403 si no es is_super_owner=true en resellers. No modifica auth_utils (fail-safe)."""
    user = await get_current_user(authorization)
    if not await is_super_owner_id(user["id"]):
        raise HTTPException(status_code=403, detail="super_owner_only")
    return user
