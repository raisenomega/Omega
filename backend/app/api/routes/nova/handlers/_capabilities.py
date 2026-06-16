"""Inventario de capacidades reales desplegadas · autoconciencia de NOVA (Punto 6).

NOVA alucinaba "~35% completo" porque su system NO tenía inventario de lo VIVO. Este bloque le da
la verdad del deploy: numéricos derivados en vivo (git_sha env · CHAINS · roster canónico · SENTINEL
score · veredictos reales) + manifiesto curado VIVO/NO-HECHO. Cero % de completitud inventado (P1):
dice lo que está vivo Y lo que falta. Cacheado (TTL 10min · el system se arma por mensaje).
DDD: api/handlers (misma capa que _context_builder · no toca persona/domain). Fail-safe POR query.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional

from app.agents.orchestrator_agent import OrchestratorAgent
from app.bc_cognition.domain.canonical_agents import CANONICAL_AGENTS
from app.bc_cognition.application.nova_aria_learning import _is_real_verdict
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_TTL_SECONDS = 600  # 10 min · el system del chat se arma en cada mensaje
_cache: Optional[str] = None
_cache_time: Optional[datetime] = None

# ⚠️ MANIFIESTO CURADO · ACTUALIZAR POR MILESTONE. Las líneas VIVO/NO-HECHO declaran la verdad del
# deploy (NO se derivan del código · derivarlas en runtime sería frágil). Reglas de mantenimiento:
#   · al cerrar el loop de verdad (Punto 0) → mover la línea "Loop de verdad" de NO-HECHO a VIVO.
#   · al hacer GAP-2 / 2.1 → quitar esas líneas de NO-HECHO.
_VIVO_CURADO = [
    "Memoria: agent_memory activa · eslabón ARIA→NOVA wired (leés el stream de ARIA por negocio)",
    "Contexto: client_id explícito del Business Switcher wired (2.0)",
]
_NO_HECHO_CURADO = [
    "NO orquestás chains desde este chat (GAP-2) — el orchestrator vive en sus endpoints",
    "NO hay detección de intención/workflow desde el chat (2.1)",
    "Islas de naming legacy sin reconciliar (F1.5)",
]

# Regla P1: prohíbe AGREGAR un juicio de completitud (no solo el símbolo %). Un grado global de
# completitud es un dato sintético en un dashboard de autoconocimiento → exactamente lo que P1 veta.
_REGLA_P1 = (
    "No inventes un grado de completitud global (porcentaje, fracción, ni etiqueta tipo 'medio/alto') "
    "— esa métrica no existe. Cuando te pregunten qué tan completo estás, respondé enumerando qué "
    "capacidades están vivas y cuáles no, sin agregarlas en un puntaje."
)


def _sentinel_score(client) -> str:
    """Último security_score de SENTINEL · fail-safe propio → 'n/d'."""
    if client is None:
        return "n/d"
    try:
        r = client.table("sentinel_scans").select("security_score")\
            .order("created_at", desc=True).limit(1).execute().data
        return str(r[0]["security_score"]) if r and r[0].get("security_score") is not None else "n/d"
    except Exception as e:
        logger.warning(f"capabilities: sentinel_score falló: {e}")
        return "n/d"


def _real_verdicts(client) -> str:
    """Conteo en vivo de interacciones ARIA con veredicto de calidad real · fail-safe propio → 'n/d'.
    Sube solo cuando se cierre el loop de verdad (Punto 0), sin tocar este bloque."""
    if client is None:
        return "n/d"
    try:
        rows = client.table("agent_memory").select("was_correct, decision")\
            .eq("agent_code", "aria").not_.is_("was_correct", "null").execute().data or []
        return str(sum(1 for r in rows if _is_real_verdict(r)))
    except Exception as e:
        logger.warning(f"capabilities: real_verdicts falló: {e}")
        return "n/d"


def build_capabilities_block() -> str:
    """Bloque 'INVENTARIO DE CAPACIDADES' · cacheado 10min. Las 2 queries (score · veredictos) tienen
    fail-safe independiente: una falla → 'n/d' en SU línea, el bloque siempre se renderiza."""
    global _cache, _cache_time
    now = datetime.now(timezone.utc)
    if _cache is not None and _cache_time and (now - _cache_time).total_seconds() < _TTL_SECONDS:
        return _cache

    sha = os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:7]
    chains = list(OrchestratorAgent.CHAINS.keys())
    ops = [code for code, a in CANONICAL_AGENTS.items() if a["status"] == "operational"]
    try:
        client = get_supabase_service().client
    except Exception as e:
        logger.warning(f"capabilities: supabase no disponible: {e}")
        client = None

    vivo = [
        f"Orquestación: {len(chains)} chains operativas ({', '.join(chains)}) vía /orchestrator y /agents",
        f"Agentes: {len(ops)} operativos ({', '.join(ops)}) + SOPHIA latente + GUARDIAN subsistema",
        f"Seguridad: SENTINEL security_score {_sentinel_score(client)}/100",
        *_VIVO_CURADO,
    ]
    no_hecho = [
        *_NO_HECHO_CURADO,
        f"Loop de verdad: {_real_verdicts(client)} interacciones con veredicto real cerrado",
    ]
    block = (
        f"\n\n=== INVENTARIO DE CAPACIDADES (estado real desplegado · git {sha}) ===\n"
        f"{_REGLA_P1}\n"
        "VIVO Y VERIFICADO:\n" + "\n".join(f"- {l}" for l in vivo) +
        "\n\nAÚN NO HECHO (no asumas que existe):\n" + "\n".join(f"- {l}" for l in no_hecho)
    )
    _cache, _cache_time = block, now
    return block
