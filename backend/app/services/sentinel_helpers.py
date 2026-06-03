"""
SENTINEL Helpers — Shared scoring utilities
Importado por sentinel_vault, sentinel_pulse, sentinel_db.
MAX 200L — R-LINES-001
"""
import hashlib


def issue_hash(severity: str, type_: str, message: str) -> str:
    """Identidad estable de un issue cross-scan · sha256(severity|type|message).

    Una sola fuente de verdad: ignore_issue, dispatch_fix y el join de get_history
    DEBEN usar este mismo hash o el join se rompe.
    """
    return hashlib.sha256(f"{severity}|{type_}|{message}".encode()).hexdigest()


def _calculate_score(issues: list) -> int:
    """
    Score = 100 - 25*CRITICAL - 10*HIGH.
    Mínimo 0.
    """
    critical = len([i for i in issues if i["severity"] == "CRITICAL"])
    high = len([i for i in issues if i["severity"] == "HIGH"])
    return max(0, 100 - (critical * 25) - (high * 10))


def _get_status(score: int) -> str:
    """
    critical  → score < 70
    warning   → 70 <= score < 85
    pass      → score >= 85
    """
    return "critical" if score < 70 else "warning" if score < 85 else "pass"
