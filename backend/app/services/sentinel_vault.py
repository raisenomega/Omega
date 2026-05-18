"""
SENTINEL VAULT — Secret & Env Var Security
Verifica presencia, formato y fortaleza de variables críticas.
MAX 200L — R-LINES-001
"""
import os
import time
import logging
from typing import Dict, Any

from app.services.sentinel_helpers import _calculate_score, _get_status

logger = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────

REQUIRED_VARS = [
    "ANTHROPIC_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SECRET_KEY",
    "JWT_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "TAVILY_API_KEY",
]

FORMAT_CHECKS: Dict[str, Any] = {
    "SUPABASE_URL":       lambda v: v.startswith("https://"),
    "ANTHROPIC_API_KEY":  lambda v: v.startswith("sk-ant-"),
}

MIN_LENGTH = {
    "SECRET_KEY":     32,
    "JWT_SECRET_KEY": 32,
}


# ── SCAN ──────────────────────────────────────────────────────

async def run_vault_scan() -> Dict[str, Any]:
    """
    Detecta secrets expuestos y verifica env vars.

    Checks:
      1. Presencia   → CRITICAL MISSING_ENV_VAR
      2. Formato     → HIGH    INVALID_FORMAT
      3. Fortaleza   → HIGH    WEAK_SECRET
    """
    start = time.time()
    issues = []

    # 1 — Presence
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            issues.append({
                "severity": "CRITICAL",
                "type": "MISSING_ENV_VAR",
                "message": f"{var} no configurada",
            })

    # 2 — Format
    for var, check in FORMAT_CHECKS.items():
        val = os.getenv(var, "")
        if val and not check(val):
            issues.append({
                "severity": "HIGH",
                "type": "INVALID_FORMAT",
                "message": f"{var} formato invalido",
            })

    # 3 — Minimum length
    for var, min_len in MIN_LENGTH.items():
        val = os.getenv(var, "")
        if val and len(val) < min_len:
            issues.append({
                "severity": "HIGH",
                "type": "WEAK_SECRET",
                "message": f"{var} demasiado corto ({len(val)} < {min_len})",
            })

    score = _calculate_score(issues)
    return {
        "agent_code": "VAULT",
        "scan_type": "security",
        "status": _get_status(score),
        "security_score": score,
        "issues": issues,
        "scan_duration_ms": int((time.time() - start) * 1000),
        "deploy_decision": "BLOCK" if score < 70 else "APPROVE",
    }
