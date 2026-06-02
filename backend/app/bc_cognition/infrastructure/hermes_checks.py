"""HERMES Capa 1 · chequeo LIVIANO de salud de integraciones externas (CORE fase 1).

Registra en mcp_health_log el estado de cada integración viva SIN llamadas externas que
cuesten tokens/cuota (H7 · regla de costos): solo mira si la credencial está presente en el
entorno. 'ok' = credencial truthy · 'no_configurado' = vacía. El estado 'last_use_failed' y la
columna last_use llegan en fase 1.5 (DEBT-HERMES-USAGE-TRACKING · instrumentar adapters).
Best-effort: un fallo de insert se loguea, NUNCA rompe el cron (igual que aria_repository)."""
import asyncio
import logging
import os
from datetime import datetime, timezone
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# 8 integraciones vivas → env var de su credencial. Las aspiracionales (Tavily/Exa/Firecrawl/
# Apify) NO entran (no existen en código). Google/Meta fuera de fase 1 (503 sin creds).
_INTEGRATIONS: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "nano_banana": "GEMINI_API_KEY",
    "veo3": "GEMINI_API_KEY",
    "voyage": "VOYAGE_API_KEY",
    "brave": "BRAVE_API_KEY",
    "stripe": "STRIPE_SECRET_KEY",
    "resend": "RESEND_API_KEY",
    "zernio": "ZERNIO_API_KEY",        # F5 · publicación social per-negocio
}


def build_health_rows() -> list[dict[str, object]]:
    """Estado liviano de cada integración (puro · sin I/O externo · testeable)."""
    rows: list[dict[str, object]] = []
    for name, env_var in _INTEGRATIONS.items():
        configured = bool((os.environ.get(env_var) or "").strip())
        rows.append({
            "integration": name,
            "status": "ok" if configured else "no_configurado",
            "detail": None if configured else f"{env_var} ausente en el entorno",
            "last_use": None,  # fase 1.5 · DEBT-HERMES-USAGE-TRACKING
        })
    return rows


def _apply_check(sb, integration: str, status: str, detail: str | None) -> str:
    """Cron insert-on-change. Mismo estado → UPDATE checked_at PRESERVANDO last_use (el cron es un
    CHEQUEO de config, NO un uso · no debe pisar el last_use real del usage-tracking). Estado cambió
    (o primera vez) → INSERT (last_use=None). H7: si la última fila es 'last_use_failed' (caída real
    detectada por el usage), 'ok' por sola config-presente NO la tapa → solo refresca checked_at (la
    miré) sin cambiar status ni last_use. Evita inflar la tabla y no enmascara un fallo de uso real."""
    now = datetime.now(timezone.utc).isoformat()
    last = sb.table("mcp_health_log").select("id,status").eq(
        "integration", integration).order("checked_at", desc=True).limit(1).execute()
    prev = last.data[0] if last.data else None
    prev_status = prev.get("status") if prev else None
    # H7: no tapar un fallo real del usage con 'ok' por sola config presente.
    no_tapar = prev_status == "last_use_failed" and status == "ok"
    if prev and (prev_status == status or no_tapar):
        sb.table("mcp_health_log").update({"checked_at": now}).eq("id", prev["id"]).execute()  # NO toca last_use ni status
        return "update"
    sb.table("mcp_health_log").insert({
        "integration": integration, "status": status, "detail": detail, "last_use": None,
    }).execute()
    return "insert"


def _run_checks_sync(sb, rows: list[dict[str, object]]) -> int:
    """Aplica _apply_check por integración (best-effort por fila · una rota no corta las otras)."""
    inserted = 0
    for r in rows:
        try:
            if _apply_check(sb, str(r["integration"]), str(r["status"]), r["detail"]) == "insert":
                inserted += 1
        except Exception as e:
            logger.warning(f"hermes_ping · {r['integration']} skip (best-effort): {e}")
    return inserted


async def run_hermes_ping() -> dict[str, int]:
    """Cron HERMES Capa 1 (cada 5 min): insert-on-change por integración en mcp_health_log.
    Best-effort: si Supabase falla, log + retorna conteo · nunca propaga al scheduler."""
    rows = build_health_rows()
    ok = sum(1 for r in rows if r["status"] == "ok")
    try:
        sb = get_supabase_service().client
        inserted = await asyncio.to_thread(_run_checks_sync, sb, rows)
    except Exception as e:
        logger.error(f"hermes_ping · mcp_health_log failed: {e}", exc_info=True)
        return {"checked": len(rows), "ok": ok, "inserted": 0}
    logger.info(f"hermes_ping · checked={len(rows)} ok={ok} inserted={inserted} updated={len(rows) - inserted}")
    return {"checked": len(rows), "ok": ok, "inserted": inserted}
