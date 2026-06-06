"""Fase 1 commit 4 · roster de NOVA desde CANONICAL_AGENTS (no la tabla muerta omega_agents)."""
import asyncio
from unittest.mock import patch

from app.api.routes.nova.handlers import _context_builder as cb
from app.api.routes.nova.handlers import get_briefing as gb

_CODES = ("nova_chat", "orchestrator", "content_creator", "strategy",
          "brand_voice", "analytics", "crisis_manager", "sentinel_security")


def test_get_agents_context_canonical():
    cb._agents_cache = None; cb._agents_cache_time = None
    ctx = asyncio.run(cb.get_agents_context())
    assert ctx.strip()
    assert "45" not in ctx and "37" not in ctx
    for code in _CODES:
        assert code in ctx
    assert "SOPHIA" in ctx and "GUARDIAN" in ctx and "ARIA" in ctx


def test_get_agents_context_no_db():
    """Prueba que NO consulta DB: si llamara get_supabase_service, esto reventaría."""
    cb._agents_cache = None; cb._agents_cache_time = None
    with patch.object(cb, "get_supabase_service", side_effect=AssertionError("no DB")):
        ctx = asyncio.run(cb.get_agents_context())
    assert "nova_chat" in ctx and "8 operativos" in ctx


class _FakeQ:
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def execute(self): return type("R", (), {"data": [], "count": 0})()


class _FakeClient:
    def table(self, name): return _FakeQ()


class _FakeSvc:
    client = _FakeClient()


def test_briefing_uses_canonical_roster():
    with patch.object(gb, "get_supabase_service", return_value=_FakeSvc()):
        out = asyncio.run(gb.handle_get_briefing())
    assert out["system_status"]["agents_registered"] == 8
    assert len(out["active_agents"]) == 8
    assert {a["code"] for a in out["active_agents"]} == set(_CODES)


# ── Commit 2 · sección 8 "aria_learning" (eslabón 3) vía la fachada ──
_FAKE_ARIA = {"businesses": [{"client_id": "afb9f578", "name": "Zafacones Ramos",
              "total": 88, "with_real_verdict": 0, "no_signal": 88}], "grand_total": 109}


def test_briefing_includes_aria_learning_section():
    with patch.object(gb, "get_supabase_service", return_value=_FakeSvc()), \
         patch.object(gb, "aria_learning_global", return_value=_FAKE_ARIA):
        out = asyncio.run(gb.handle_get_briefing())
    # sección 8 poblada vía la fachada
    assert out["aria_learning"] == _FAKE_ARIA
    assert out["aria_learning"]["grand_total"] == 109
    # las otras 7 secciones siguen presentes (no rotas)
    for key in ("nova_memory", "system_status", "active_agents", "departments",
                "context_documents", "pending_alerts", "prompt_vault_stats"):
        assert key in out
    assert len(out["active_agents"]) == 8  # roster canónico Fase 1 intacto
