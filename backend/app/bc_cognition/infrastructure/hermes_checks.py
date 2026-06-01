"""HERMES Capa 1 · chequeo LIVIANO de salud de integraciones externas (CORE fase 1).

Registra en mcp_health_log el estado de cada integración viva SIN llamadas externas que
cuesten tokens/cuota (H7 · regla de costos): solo mira si la credencial está presente en el
entorno. 'ok' = credencial truthy · 'no_configurado' = vacía. El estado 'last_use_failed' y la
columna last_use llegan en fase 1.5 (DEBT-HERMES-USAGE-TRACKING · instrumentar adapters).
Best-effort: un fallo de insert se loguea, NUNCA rompe el cron (igual que aria_repository)."""
import asyncio
import logging
import os
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# 7 integraciones vivas → env var de su credencial. Las aspiracionales (Zernio/Tavily/Exa/
# Firecrawl/Apify) NO entran (no existen en código). Google/Meta fuera de fase 1 (503 sin creds).
_INTEGRATIONS: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "nano_banana": "GEMINI_API_KEY",
    "veo3": "GEMINI_API_KEY",
    "voyage": "VOYAGE_API_KEY",
    "brave": "BRAVE_API_KEY",
    "stripe": "STRIPE_SECRET_KEY",
    "resend": "RESEND_API_KEY",
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


async def run_hermes_ping() -> dict[str, int]:
    """Cron HERMES Capa 1 (cada 5 min): arma estados y los registra en mcp_health_log.
    Best-effort: si el insert falla, log + retorna conteo · nunca propaga al scheduler."""
    rows = build_health_rows()
    ok = sum(1 for r in rows if r["status"] == "ok")
    try:
        sb = get_supabase_service().client
        await asyncio.to_thread(lambda: sb.table("mcp_health_log").insert(rows).execute())
    except Exception as e:
        logger.error(f"hermes_ping · insert mcp_health_log failed: {e}", exc_info=True)
        return {"checked": len(rows), "ok": ok, "inserted": 0}
    logger.info(f"hermes_ping · checked={len(rows)} ok={ok} no_configurado={len(rows) - ok}")
    return {"checked": len(rows), "ok": ok, "inserted": len(rows)}
