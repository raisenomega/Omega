"""POST /api/v1/aria/suggestions · genera Next-Best-Action proactivo (rule-based · I1 N/A).

Evalúa 4 reglas sobre señales reales · inserta solo las que faltan (idempotente:
skip si ya hay una is_read=false del mismo tipo). Conservador (P1): señal indeterminada
→ NO se emite. Escritura con service_role vía _suggestions_repository.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from fastapi import APIRouter, Header
from app.api.routes.aria_v1.models import (
    ARIASuggestionsCreateRequest, ARIASuggestion, ARIASuggestionsResponse,
)
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.bc_cognition.infrastructure import _suggestions_repository as repo
from app.bc_cognition.infrastructure import _suggestions_writer as writer

router = APIRouter()
logger = logging.getLogger(__name__)

_INACTIVITY_DAYS = 3
_PROFILE_FIELDS = ("business_email", "website", "industry")
_MSG = {
    "inactivity": "Hace varios días que no publicás. ¿Generamos contenido fresco?",
    "upgrade_plan": "Con el plan PRO desbloqueás posts ilimitados y más cuentas. ¿Lo vemos?",
    "profile_incomplete": "Completá tu perfil para que ARIA genere contenido más afinado.",
    "no_addons": "Probá ARIA Premium para respuestas más inteligentes en tu asistente.",
}


def _wants_inactivity(client_id: str) -> Optional[bool]:
    determinable, last = repo.published_signal(client_id)
    if not determinable:
        return None  # consulta falló · indeterminado · P1 (ni emite ni retracta)
    if last is None:
        return True  # nunca publicó · aplica
    return datetime.now(timezone.utc) - last >= timedelta(days=_INACTIVITY_DAYS)


def _wants_upgrade(client_id: str) -> Optional[bool]:
    plan = repo.client_plan(client_id)
    if plan is None:
        return None  # consulta falló o sin fila · indeterminado · P1
    return plan == "basic"  # basic→aplica · otro plan conocido→negativo DETERMINADO (retracta)


def _wants_profile_incomplete(client: dict[str, Any]) -> Optional[bool]:
    filled = sum(1 for f in _PROFILE_FIELDS if str(client.get(f) or "").strip())
    return filled < 2  # client ya resuelto → siempre determinado


def _wants_no_addons(client: dict[str, Any]) -> Optional[bool]:
    level = client.get("aria_level")
    if not isinstance(level, int):
        return None  # nivel indeterminado · P1
    return level < 4  # aria_level >= 4 = ARIA Premium


def _rule_states(client: dict[str, Any]) -> dict[str, Optional[bool]]:
    """Tri-estado por tipo · True=aplica (emitir) · False=negativo DETERMINADO (retractar stale) ·
    None=indeterminado (no tocar). Orden estable."""
    cid = str(client["id"])
    return {
        "inactivity": _wants_inactivity(cid),
        "upgrade_plan": _wants_upgrade(cid),
        "profile_incomplete": _wants_profile_incomplete(client),
        "no_addons": _wants_no_addons(client),
    }


@router.post("/suggestions", response_model=ARIASuggestionsResponse)
async def aria_suggestions_create(
    request: ARIASuggestionsCreateRequest,
    authorization: Optional[str] = Header(None),
) -> ARIASuggestionsResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)
    cid = str(client["id"])
    generated = 0
    for stype, applies in _rule_states(client).items():
        if applies is True:
            if repo.unread_type_exists(cid, stype):
                continue  # idempotente · ya hay una sin leer de este tipo
            if writer.insert_suggestion(cid, user.get("id"), _MSG[stype], stype):
                generated += 1
        elif applies is False:
            # Retracción: el tipo dejó de aplicar de forma DETERMINADA (ej. basic→enterprise)
            # → auto-cierra las unread stale de ese tipo para ESE negocio. None→no toca (P1).
            writer.retract_unread(cid, stype)
    rows = writer.list_suggestions(cid, unread_only=False)
    return ARIASuggestionsResponse(
        suggestions=[ARIASuggestion(**r) for r in rows], generated=generated,
    )
