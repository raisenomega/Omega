"""Eslabón 3 · Commit 3 · build_nova_system_prompt inyecta el bloque "Aprendizaje de ARIA" per-negocio
cuando hay client_id (de 2.0). Persona/roster intactos · conteos honestos · token budget respetado."""
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from app.api.routes.nova.handlers import _context_builder as cb
from app.bc_cognition.domain.persona_nova import NOVA_SYSTEM_PROMPT

_LEARN = {"client_id": "afb9f578", "counts": {"total": 88, "with_real_verdict": 1, "no_signal": 87},
          "interactions": [
              {"context_snippet": "¿A qué se dedica mi negocio?", "decision_snippet": "Mantenimiento de zafacones.",
               "was_correct": None, "created_at": "t"},
              {"context_snippet": "Dame ideas", "decision_snippet": "Antes/después de limpieza.",
               "was_correct": True, "created_at": "t"}]}
_EMPTY = {"client_id": "c1", "interactions": [], "counts": {"total": 0, "with_real_verdict": 0, "no_signal": 0}}


def _build(client_id=None, learning=_LEARN):
    cb._agents_cache = None; cb._agents_cache_time = None
    with patch.object(cb, "ContextService") as CS, \
         patch.object(cb, "aria_learning_for_client", return_value=learning), \
         patch.object(cb, "get_supabase_service", return_value=MagicMock()):
        CS.return_value.get_global_context = AsyncMock(return_value="")
        return asyncio.run(cb.build_nova_system_prompt("", [], active_client="", client_id=client_id))


def test_block_present_with_client_id():
    sys = _build("afb9f578")
    assert "APRENDIZAJE DE ARIA" in sys
    assert "Mantenimiento de zafacones." in sys            # snippet real de ARIA
    assert "88 interacciones · 1 con veredicto real · 87 sin señal" in sys  # conteos honestos


def test_no_block_without_client_id():
    assert "APRENDIZAJE DE ARIA" not in _build(None)


def test_no_block_when_facade_empty():
    assert "APRENDIZAJE DE ARIA" not in _build("c1", _EMPTY)  # sin inventar


def test_render_has_no_percentage_or_accuracy():
    sys = _build("afb9f578")
    block = sys[sys.index("APRENDIZAJE DE ARIA"):]
    assert "%" not in block and "accuracy" not in block.lower()


def test_persona_and_roster_intact():
    sys = _build("afb9f578")
    assert sys.startswith(NOVA_SYSTEM_PROMPT)   # persona Fase 1 intacta, como prefijo
    assert "nova_chat" in sys                   # roster canónico presente


def test_token_budget_truncates_aria_first():
    base = _build(None)  # system sin bloque ARIA = los bloques de prioridad
    big = {"client_id": "c1", "counts": {"total": 8, "with_real_verdict": 0, "no_signal": 8},
           "interactions": [{"context_snippet": "x" * 150, "decision_snippet": "y" * 150,
                             "was_correct": None, "created_at": "t"} for _ in range(8)]}
    with patch.object(cb, "MAX_CONTEXT_CHARS", len(base) + 40):
        sys = _build("c1", big)
    assert len(sys) <= len(base) + 40   # el bloque ARIA se truncó para no exceder MAX
