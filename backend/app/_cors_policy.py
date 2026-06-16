"""Política CORS · fail-secure (P1-7). Separado de config.py porque config vive
crónicamente en su techo C4 (100L · reference config.py techo C4) · meter la
función ahí lo empujaba a >100 (push bloqueado)."""
from typing import List


def resolve_cors_origins(origins: List[str], environment: str) -> List[str]:
    """Vacío en PRODUCCIÓN → raise (jamás wildcard en prod · un typo en la env var
    abriría CORS al mundo). Dev → ['*'] explícito. Con orígenes → tal cual."""
    if origins:
        return origins
    if environment == "production":
        raise RuntimeError(
            "BACKEND_CORS_ORIGINS vacía en producción · fail-secure: configurá los "
            "orígenes permitidos (CSV) en la env var · jamás wildcard en prod."
        )
    return ["*"]
