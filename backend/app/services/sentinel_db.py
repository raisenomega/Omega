"""
SENTINEL DB GUARDIAN — Database Health & Integrity
Verifica accesibilidad de tablas críticas y conteos mínimos.
MAX 200L — R-LINES-001
"""
import time
import logging
from typing import Dict, Any

from app.infrastructure.supabase_service import get_supabase_service
from app.services.sentinel_helpers import _calculate_score, _get_status

logger = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────

# Todas las tablas que deben existir y ser accesibles.
# Cada entrada verificada contra supabase/migrations/ (cero check fantasma · P1).
TABLES_CRITICAL = [
    # Core operativo
    "agents",          # 00001:255 CREATE TABLE agents
    "agent_memory",    # 00002:12  (era 'omega_agent_memory' fantasma)
    "resellers",       # 00001:39
    "clients",         # 00001:94
    # Funcionalidad
    "scheduled_posts",  # 00001:229
]

# Tablas con un mínimo de filas esperadas
MIN_COUNTS = {
    "agents":    1,  # era 'omega_agents': 44 · tabla real · solo verifica que tenga filas
    "clients":   1,
    "resellers": 1,
}


# ── SCAN ──────────────────────────────────────────────────────

async def run_db_guardian() -> Dict[str, Any]:
    """
    Verifica salud e integridad de la base de datos.

    Checks:
      1. Accesibilidad → CRITICAL MISSING_TABLE  (SELECT id LIMIT 1)
      2. Conteos mín.  → HIGH    DATA_INTEGRITY  (count < expected)
    """
    start = time.time()
    supabase = get_supabase_service()
    issues = []

    # 1 — Table accessibility
    for table in TABLES_CRITICAL:
        try:
            supabase.client.table(table).select("id").limit(1).execute()
        except Exception:
            issues.append({
                "severity": "CRITICAL",
                "type": "MISSING_TABLE",
                "message": f"{table} no accesible",
            })

    # 2 — Minimum row counts
    for table, min_count in MIN_COUNTS.items():
        try:
            result = supabase.client.table(table).select("id", count="exact").execute()
            actual = result.count or 0
            if actual < min_count:
                issues.append({
                    "severity": "HIGH",
                    "type": "DATA_INTEGRITY",
                    "message": f"{table}: {actual} filas (mín {min_count})",
                })
        except Exception as e:
            logger.error(f"Count check error {table}: {e}")

    score = _calculate_score(issues)
    return {
        "agent_code": "DB_GUARDIAN",
        "scan_type": "db",
        "status": _get_status(score),
        "security_score": score,
        "issues": issues,
        "scan_duration_ms": int((time.time() - start) * 1000),
        "deploy_decision": "BLOCK" if score < 70 else "APPROVE",
    }
