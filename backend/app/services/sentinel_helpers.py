"""
SENTINEL Helpers — Shared scoring utilities
Importado por sentinel_vault, sentinel_pulse, sentinel_db.
MAX 200L — R-LINES-001
"""


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
