"""Bug tz (11 jun) · scheduled_for DEBE ser tz-aware · naive → 422 (fail-honest).

El frontend manda la hora local del usuario como UTC explícito (Z u offset); el
backend NUNCA asume UTC para un naive (eso causaba el corrimiento de -4h AST:
owner escribe 09:45 → se guardaba 09:45 UTC → calendario renderiza 05:45 AST)."""
import pytest
from pydantic import ValidationError

from app.api.routes.calendar_v3.models.calendar_models import ScheduledPostV3Create

_BASE = {"client_id": "c1", "platform": "instagram", "content_ids": ["x"]}


def test_naive_rechazado_422():
    with pytest.raises(ValidationError):
        ScheduledPostV3Create(**_BASE, scheduled_for="2026-06-13T13:00:00")  # sin offset


def test_aware_z_aceptado_es_utc():
    m = ScheduledPostV3Create(**_BASE, scheduled_for="2026-06-13T17:00:00Z")
    assert m.scheduled_for.tzinfo is not None
    assert m.scheduled_for.utcoffset().total_seconds() == 0


def test_aware_offset_ast_aceptado():
    m = ScheduledPostV3Create(**_BASE, scheduled_for="2026-06-13T13:00:00-04:00")
    assert m.scheduled_for.utcoffset().total_seconds() == -4 * 3600


# ─── "AMBAS" · placement enum + alias is_story deprecado (deploy-skew safe) ───
_AWARE = {"scheduled_for": "2026-06-13T17:00:00Z"}


def test_placement_default_feed():
    """Sin placement ni is_story → 'feed' (retrocompat · flujo de hoy)."""
    m = ScheduledPostV3Create(**_BASE, **_AWARE)
    assert m.placement == "feed"


def test_placement_explicito_both():
    m = ScheduledPostV3Create(**_BASE, **_AWARE, placement="both")
    assert m.placement == "both"


def test_is_story_alias_deriva_story():
    """Deploy-skew: front viejo manda is_story=True (sin placement) → placement='story'."""
    m = ScheduledPostV3Create(**_BASE, **_AWARE, is_story=True)
    assert m.placement == "story"


def test_placement_explicito_gana_sobre_alias():
    """Si llega placement explícito, manda él (el alias no lo pisa)."""
    m = ScheduledPostV3Create(**_BASE, **_AWARE, placement="both", is_story=True)
    assert m.placement == "both"


def test_placement_invalido_rechazado():
    with pytest.raises(ValidationError):
        ScheduledPostV3Create(**_BASE, **_AWARE, placement="carrusel")
