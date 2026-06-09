"""Resolucion del accountId de Zernio por plataforma · BINDING DETERMINISTICO per-negocio (post-incidente).

INCIDENTE FUGA MULTI-TENANT (8 jun 2026): el fallback 2a "en vivo" (consultar list_accounts() y, si habia
UNA sola cuenta de la plataforma, usarla) publicaba el contenido de CUALQUIER negocio en la unica cuenta
del workspace. Caso real: un post de "Mail Boxes Design" (zernio_account_id=NULL) salio en la IG de RAISEN
(@raisenagency) porque era la unica cuenta IG bajo la key. El "1 match → usala" se rompe apenas existe un
segundo negocio. ELIMINADO.

REGLA AHORA (zero-ambiguedad a cualquier escala): la cuenta Zernio se resuelve SOLO via binding
determinístico per-negocio (`mapped_account_id` = zernio_account_id guardado en social_accounts del
negocio activo, capturado al CONECTAR la cuenta · jamas adivinado por handle ni por "la unica del
workspace"). Sin binding → FALLA HONESTO (el caller lo mapea a 'conecta esta red para este negocio').
El binding real (conexion + captura del id) es la arquitectura multi-tenant (DEBT-MULTITENANT-ZERNIO).
"""
from typing import Optional

from app.bc_cognition.infrastructure.zernio_adapter import ZernioPublishError


class ZernioAccountResolutionError(ZernioPublishError):
    """No hay binding determinístico de cuenta Zernio para (negocio, plataforma) · cero adivinanza."""


async def resolve_account_id(platform: str, mapped_account_id: Optional[str] = None) -> str:
    """Devuelve el _id de la cuenta Zernio para `platform` SOLO via binding per-negocio.
    `mapped_account_id` = zernio_account_id del negocio activo (lo lee el caller de social_accounts).
    Sin binding (None/vacio) → ZernioAccountResolutionError (NO se adivina · cierra la fuga multi-tenant).
    El fallback 2a 'en vivo a la unica cuenta del workspace' fue ELIMINADO (ver docstring del modulo)."""
    if mapped_account_id:
        return str(mapped_account_id)
    raise ZernioAccountResolutionError(f"zernio_sin_cuenta:{platform}")
