"""GET /guardian/user-detail/{user_id} · detalle completo para el modal · owner-only.

Resuelve email vía auth.admin (no seleccionable por PostgREST) + último login (ip/país/session/UA)
+ historial 20 events + incidents abiertos + IPs del user que están en watchlist.
"""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.infrastructure.supabase_service import get_supabase_service


async def handle_user_detail(user_id: str, authorization: Optional[str]) -> Dict[str, Any]:
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    email = account_created = last_sign_in = None
    try:
        u = sb.auth.admin.get_user_by_id(user_id)
        usr = getattr(u, "user", None)
        email = getattr(usr, "email", None)
        account_created = getattr(usr, "created_at", None)
        last_sign_in = getattr(usr, "last_sign_in_at", None)
    except Exception:  # noqa: BLE001 — user borrado/no encontrado · seguimos con el log
        pass

    events = (sb.table("user_security_log")
              .select("id, event_type, ip_address, user_agent, country, geo, session_id, risk_score, created_at")
              .eq("user_id", user_id).order("created_at", desc=True).limit(20).execute().data) or []
    last_login = next((e for e in events if e["event_type"] == "login_success"), None)
    incidents = (sb.table("security_incidents")
                 .select("id, incident_type, severity, status, summary, detected_at")
                 .eq("user_id", user_id).in_("status", ["open", "investigating"])
                 .order("detected_at", desc=True).limit(10).execute().data) or []

    ips = list({e["ip_address"] for e in events if e.get("ip_address")})
    matches = []
    if ips:
        matches = (sb.table("ip_watchlist").select("id, ip_address, list_type, reason, expires_at")
                   .in_("ip_address", ips).execute().data) or []

    return {
        "user_id": user_id, "email": email, "account_created": account_created, "last_sign_in": last_sign_in,
        "last_login": last_login, "history": events, "open_incidents": incidents, "watchlist_matches": matches,
    }
