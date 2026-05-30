"""Resolución de rol/cliente/nivel ARIA · fuente ÚNICA compartida por use_aria_message y
use_generate_strategy (anti-duplicación · evita dos copias que diverjan). Retorna
(role, client_id, reseller_id, level)."""
from typing import Optional, Tuple
from app.bc_cognition.infrastructure import aria_repository as repo


def resolve_role(supabase, user_id: str) -> Tuple[Optional[str], Optional[str], Optional[str], int]:
    """(role, client_id, reseller_id, level) · None role si el user no es cliente ni reseller."""
    c = repo.find_client_by_user(supabase, user_id)
    if c:
        return "client", c["id"], None, c.get("aria_level") or 1
    r = repo.find_reseller_by_owner(supabase, user_id)
    if r:  # DEBT-046: aria_level real (3 base · 4 si aria_premium_reseller)
        return "reseller", None, r["id"], r.get("aria_level") or 3
    return None, None, None, 0
