"""Resolucion del accountId de Zernio por plataforma · FASE 2a (SOLO-UN-NEGOCIO · en vivo).

ALCANCE INTENCIONAL (NO es bug · leer antes de "arreglar"):
2a resuelve el accountId consultando list_accounts() EN VIVO y filtrando por plataforma. Asume UN
negocio bajo la ZERNIO_API_KEY (el caso actual del owner). NO persiste nada · NO toca social_accounts
ni connection_metadata · SIN migracion.

El MULTI-NEGOCIO es FASE 5/2b: ahi se guarda el zernio_account_id por (client_id, platform) en
social_accounts.connection_metadata (columna existente · sin migracion) y se resuelve por
activeBusinessId (patron Switcher V1). HASTA ENTONCES, si hay 2+ cuentas de la MISMA plataforma bajo
la key → FALLA CLARO (P2 · proteger la marca: jamas publicar en la cuenta equivocada · mejor fallar
que adivinar). Esa rama es justo el puente a 2b.
"""
import logging

from app.bc_cognition.infrastructure.zernio_adapter import ZernioPublishError, list_accounts

logger = logging.getLogger(__name__)


class ZernioAccountResolutionError(ZernioPublishError):
    """No se pudo resolver UNA cuenta para la plataforma (0 conectadas, o 2+ ambiguas · cero adivinanza)."""


async def resolve_account_id(platform: str) -> str:
    """Devuelve el _id de la UNICA cuenta Zernio conectada para `platform` (FASE 2a · un negocio).
    0 → ZernioAccountResolutionError (no conectada) · 2+ → error (ambiguo · desambiguar = FASE 2b)."""
    accounts = await list_accounts()
    matches = [a for a in accounts if a.get("platform") == platform and a.get("_id")]
    if not matches:
        raise ZernioAccountResolutionError(f"zernio_sin_cuenta:{platform}")
    if len(matches) > 1:
        # P2: 2+ cuentas de la misma plataforma = ambiguo. NUNCA elegir una (publicar en la cuenta
        # equivocada seria el peor error). Multi-negocio resuelve esto en FASE 2b (por client_id).
        logger.warning(f"zernio resolver · {len(matches)} cuentas '{platform}' · ambiguo (2a un-negocio) → falla")
        raise ZernioAccountResolutionError(f"zernio_cuenta_ambigua:{platform}:{len(matches)}")
    return str(matches[0]["_id"])
