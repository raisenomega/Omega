"""P2 · puente aprobar draft supervisado -> calendario (scheduled_posts) · FAN-OUT por red.

Al aprobar un draft supervisado (metadata.supervisado) CON metadata.fecha_sugerida, crea 1
scheduled_post POR cada red marcada en metadata.platforms (checkboxes del modal de edicion),
cada uno con su social_account_id resuelto de la cuenta active de esa red. Cierra el ciclo ARIA:
prepara honesto -> cliente marca redes + aprueba -> aparece en el calendario, listo para publicar.

INVARIANTE (cierra sin_red de raiz): NUNCA inserta un pending con social_account_id NULL. Si ninguna
red marcada resuelve una cuenta active -> NO agenda (queda approved · falta_red) en vez de crear un
post invalido. El 'general' (sin red) cae aca: se expande en posts por-red solo cuando el cliente marca.

Decisiones owner: cuenta = primera active de (client_id, platform) · B2 (sin fecha_sugerida -> NO agenda).
"""
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.calendar_v3 import _calendar_repository as cal_repo


def _first_active_account_id(client_id: str, platform: str) -> Optional[str]:
    """Primera cuenta status='active' de la plataforma (guardrail: excluye expired/revoked/disconnected).
    None si no hay -> la red marcada se omite del fan-out (jamas se inventa cuenta)."""
    if not platform:
        return None
    sb = get_supabase_service().client
    r = sb.table("social_accounts").select("id").eq("client_id", client_id).eq(
        "platform", platform).eq("status", "active").order("created_at").limit(1).execute()
    return str(r.data[0]["id"]) if r.data else None


def _target_platforms(meta: dict[str, Any]) -> list[str]:
    """Redes marcadas (metadata.platforms · checkboxes). Back-compat: metadata.platform string si es
    red real (no 'general'/vacio). Normaliza lowercase para casar social_accounts.platform · dedup."""
    raw = meta.get("platforms")
    if isinstance(raw, list) and raw:
        plats = [str(p).strip().lower() for p in raw if str(p).strip()]
    else:
        single = str(meta.get("platform") or "").strip().lower()
        plats = [single] if single and single != "general" else []
    seen: set[str] = set()
    return [p for p in plats if not (p in seen or seen.add(p))]


def maybe_schedule_on_approve(item: dict[str, Any]) -> Optional[dict[str, Any]]:
    """supervisado + fecha_sugerida -> fan-out 1 scheduled_post por red marcada resuelta.
    None si no aplica (no supervisado / sin fecha · B2). Si aplica devuelve {scheduled, falta_red,
    scheduled_for}: scheduled=False+falta_red=True cuando ninguna red resuelve (NO inserta NULL)."""
    meta = item.get("metadata")
    if not isinstance(meta, dict) or meta.get("supervisado") is not True:
        return None
    fecha = meta.get("fecha_sugerida")
    if not fecha:
        return None  # B2: sin fecha sugerida -> no agenda · queda approved
    client_id = str(item.get("client_id") or "")
    # Pieza 2 · carrusel: deja de colapsar a [0] · propaga el array completo + doble-escritura media_url=[0].
    # Guarda `if media_urls_list else` = sin IndexError con []/None (caso borde F). media_url poblado con la
    # 1ª para que los consumidores de media_url sigan viendo 1 imagen · el publicador (capa 2) manda los N.
    media_urls_list = item.get("media_urls") or []
    media_urls_final = media_urls_list if media_urls_list else None
    media_url = media_urls_list[0] if media_urls_list else None
    rows = []
    for platform in _target_platforms(meta):
        account_id = _first_active_account_id(client_id, platform)
        if not account_id:
            continue  # red sin cuenta active -> se omite (jamas social_account_id NULL)
        rows.append({
            "client_id": client_id,
            "social_account_id": account_id,
            "content_id": str(item["id"]),
            "scheduled_for": str(fecha),
            "status": "pending",
            "media_url": media_url,
            "media_urls": media_urls_final,
        })
    if not rows:
        # 'general'/sin red marcada o ninguna resuelve -> NO agenda (queda approved · cliente marca red)
        return {"scheduled": False, "falta_red": True, "scheduled_for": str(fecha)}
    cal_repo.insert_scheduled_posts_bulk(rows)  # atomico · lanza si falla (caller best-effort)
    return {"scheduled": True, "falta_red": False, "scheduled_for": str(fecha), "count": len(rows)}
