"""P2 · puente aprobar draft supervisado → calendario (scheduled_posts).

Al aprobar un draft supervisado (metadata.supervisado) CON metadata.fecha_sugerida, lo inserta en
scheduled_posts con esa fecha → cierra el ciclo ARIA: prepara honesto → cliente aprueba → aparece en el
calendario. Conecta la fecha_sugerida que la tool de ARIA escribía sin que nadie la leyera.

Decisiones owner: A1 (primera cuenta activa de la plataforma · NULL si no hay · publisher resuelve al
publicar) · B2 (sin fecha_sugerida → NO agenda · queda approved · cliente agenda manual).
"""
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.calendar_v3 import _calendar_repository as cal_repo


def _first_active_account_id(client_id: str, platform: str) -> Optional[str]:
    """A1 · primera cuenta activa de la plataforma · None si no hay (NO lanza · publisher resuelve luego)."""
    if not platform:
        return None
    sb = get_supabase_service().client
    r = sb.table("social_accounts").select("id").eq("client_id", client_id).eq(
        "platform", platform).eq("status", "active").order("created_at").limit(1).execute()
    return str(r.data[0]["id"]) if r.data else None


def maybe_schedule_on_approve(item: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Si el draft es supervisado + tiene fecha_sugerida → inserta en scheduled_posts.
    Devuelve {scheduled_for, falta_cuenta} si agendó · None si no aplica (B2 sin fecha / no supervisado)."""
    meta = item.get("metadata")
    if not isinstance(meta, dict) or meta.get("supervisado") is not True:
        return None
    fecha = meta.get("fecha_sugerida")
    if not fecha:
        return None  # B2: sin fecha sugerida → no agenda · queda approved
    client_id = str(item.get("client_id") or "")
    account_id = _first_active_account_id(client_id, str(meta.get("platform") or ""))  # A1
    row = {
        "client_id": client_id,
        "social_account_id": account_id,   # None permitido (columna nullable · A1)
        "content_id": str(item["id"]),
        "scheduled_for": str(fecha),
        "status": "pending",
    }
    cal_repo.insert_scheduled_posts_bulk([row])  # atómico · lanza si falla (caller best-effort)
    return {"scheduled_for": str(fecha), "falta_cuenta": account_id is None}
