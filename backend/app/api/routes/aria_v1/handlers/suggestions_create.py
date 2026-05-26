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


def _wants_inactivity(client_id: str) -> bool:
    determinable, last = repo.published_signal(client_id)
    if not determinable:
        return False  # consulta falló · indeterminado · P1
    if last is None:
        return True  # nunca publicó · señal real
    return datetime.now(timezone.utc) - last >= timedelta(days=_INACTIVITY_DAYS)


def _wants_upgrade(client_id: str) -> bool:
    return repo.client_plan(client_id) == "basic"  # None (indeterminado) → no emite (P1)


def _wants_profile_incomplete(client: dict[str, Any]) -> bool:
    filled = sum(1 for f in _PROFILE_FIELDS if str(client.get(f) or "").strip())
    return filled < 2


def _wants_no_addons(client: dict[str, Any]) -> bool:
    level = client.get("aria_level")
    if not isinstance(level, int):
        return False  # nivel indeterminado · P1
    return level < 4  # aria_level >= 4 = ARIA Premium


def _evaluate(client: dict[str, Any]) -> list[str]:
    """Tipos que aplican según señales reales · orden estable."""
    cid = str(client["id"])
    rules: list[tuple[str, bool]] = [
        ("inactivity", _wants_inactivity(cid)),
        ("upgrade_plan", _wants_upgrade(cid)),
        ("profile_incomplete", _wants_profile_incomplete(client)),
        ("no_addons", _wants_no_addons(client)),
    ]
    return [t for t, applies in rules if applies]


@router.post("/suggestions", response_model=ARIASuggestionsResponse)
async def aria_suggestions_create(
    request: ARIASuggestionsCreateRequest,
    authorization: Optional[str] = Header(None),
) -> ARIASuggestionsResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)
    cid = str(client["id"])
    generated = 0
    for stype in _evaluate(client):
        if repo.unread_type_exists(cid, stype):
            continue  # idempotente · ya hay una sin leer de este tipo
        if writer.insert_suggestion(cid, user.get("id"), _MSG[stype], stype):
            generated += 1
    rows = writer.list_suggestions(cid, unread_only=False)
    return ARIASuggestionsResponse(
        suggestions=[ARIASuggestion(**r) for r in rows], generated=generated,
    )
