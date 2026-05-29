"""Fase 1 PASO 2 · tests del loop + tool prepare_supervised_draft (red · cero API real).
Mock de generate y del repo. Anti-G5: client_id de sesión, nunca de tool_input. G9 exime tests."""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.bc_cognition.application import _aria_tools as at
from app.bc_cognition.infrastructure._anthropic_types import ClaudeResponse


def _resp(text="ok", tool_calls=None):
    return ClaudeResponse(text=text, model_used="m", input_tokens=1, output_tokens=1,
                          cost_usd=0.0, latency_ms=1, cache_hit=False, tool_calls=tool_calls)


def _tool_block(tool_input):
    b = MagicMock(); b.type = "tool_use"; b.id = "tu_1"; b.name = "prepare_supervised_draft"; b.input = tool_input
    return b


def _run(client_id, gen_side_effect, insert_mock):
    """Parchea generate (side_effect = lista de respuestas) + insert_generated_content."""
    at.generate = AsyncMock(side_effect=gen_side_effect)
    at.cl_repo.safe_insert = AsyncMock(side_effect=lambda label, fn, *a, **k: insert_mock(*a, **k))
    return asyncio.run(at.run_tool_loop("aria_2", "sys", [{"role": "user", "content": "x"}], client_id))


def test_no_tool_use_is_plain_conversation():
    captured = MagicMock(return_value="cid")
    text, err = _run("client-A", [( _resp(text="hola"), None )], captured)
    assert err is None and text == "hola"
    captured.assert_not_called()  # sin tool_use → NO crea draft (idéntico a hoy)


def test_tool_use_creates_supervised_draft():
    captured = {}
    def _insert(client_id, payload):
        captured["client_id"] = client_id; captured["payload"] = payload
        return "new-cid"
    block = _tool_block({"texto": "Post de prueba", "fecha_sugerida": "2026-06-01T15:00"})
    text, err = _run("client-A",
                     [( _resp(tool_calls=[block]), None ), ( _resp(text="lo dejé en Supervisado"), None )],
                     _insert)
    assert err is None and text == "lo dejé en Supervisado"
    assert captured["client_id"] == "client-A"
    md = captured["payload"]["metadata"]
    assert md["supervisado"] is True and md["fecha_sugerida"] == "2026-06-01T15:00"
    assert captured["payload"]["status"] == "draft"


def test_anti_g5_ignores_client_id_in_params():
    captured = {}
    def _insert(client_id, payload):
        captured["client_id"] = client_id; return "cid"
    # tool_input intenta inyectar client_id de OTRO cliente
    block = _tool_block({"texto": "hack", "client_id": "client-B", "cliente": "client-B"})
    _run("client-A", [( _resp(tool_calls=[block]), None ), ( _resp(text="ok"), None )], _insert)
    assert captured["client_id"] == "client-A"  # SESIÓN · nunca B (anti-G5 demostrado)


def test_low_confidence_blocks_p3(monkeypatch):
    captured = MagicMock(return_value="cid")
    monkeypatch.setattr(at, "_DRAFT_CONFIDENCE", 5)  # < MIN_CONFIDENCE_TO_ACT (7)
    block = _tool_block({"texto": "algo"})
    text, err = _run("client-A",
                     [( _resp(tool_calls=[block]), None ), ( _resp(text="no tengo convicción"), None )],
                     captured)
    captured.assert_not_called()  # should_enqueue False → NO crea draft (P3)


def test_crisis_agent_never_enqueues_p2(monkeypatch):
    captured = MagicMock(return_value="cid")
    monkeypatch.setattr(at, "_AGENT_CODE", "crisis_manager")  # P2: prohibido en flujo auto
    block = _tool_block({"texto": "algo"})
    _run("client-A", [( _resp(tool_calls=[block]), None ), ( _resp(text="x"), None )], captured)
    captured.assert_not_called()  # should_enqueue False → NO crea (P2)


def test_tool_result_is_honest_not_hype():
    """P1: el tool_result dice 'pendiente aprobación' · NUNCA 'automátic/publica/volando'."""
    out = asyncio.run(at._execute_prepare_draft("client-A", {"texto": "post", "fecha_sugerida": "2026-06-01"}))
    msg = out["mensaje"].lower()
    assert "pendiente de aprobación" in msg and "sugerida" in msg
    assert "automátic" not in msg and "sale volando" not in msg and "se publicará hasta" in msg


def test_second_generate_gets_antihype_addendum():
    """P1: el 2º generate recibe la regla anti-hype en su system (narración honesta)."""
    at.cl_repo.safe_insert = AsyncMock(return_value="cid")
    systems = []
    async def _gen(agent_code, system, messages, max_tokens=1024, tools=None):
        systems.append(system)
        return (_resp(tool_calls=[_tool_block({"texto": "x"})]) if tools else _resp(text="ok")), None
    at.generate = _gen
    asyncio.run(at.run_tool_loop("aria_2", "BASE", [{"role": "user", "content": "x"}], "client-A"))
    assert "sale volando" in systems[1] and "requiere su aprobación" in systems[1].lower()
