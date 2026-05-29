"""Tests del loop agéntico de ARIA (run_tool_loop) · mock de generate + repo · cero API real.
Anti-G5: client_id de sesión, nunca de tool_input. `now_for` mockeado → fechas deterministas.
La creación/validación del draft se prueba en test_aria_draft.py (split C4). G9 exime tests."""
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo

from app.bc_cognition.application import _aria_tools as at
from app.bc_cognition.application import _aria_draft as d
from app.bc_cognition.infrastructure._anthropic_types import ClaudeResponse

_NOW = datetime(2026, 5, 29, 11, 0, tzinfo=ZoneInfo("America/Puerto_Rico"))


def _resp(text="ok", tool_calls=None):
    return ClaudeResponse(text=text, model_used="m", input_tokens=1, output_tokens=1,
                          cost_usd=0.0, latency_ms=1, cache_hit=False, tool_calls=tool_calls)


def _tool_block(tool_input):
    b = MagicMock(); b.type = "tool_use"; b.id = "tu_1"; b.name = "prepare_supervised_draft"; b.input = tool_input
    return b


def _run(client_id, gen_side_effect, insert_mock):
    """Parchea generate + insert + now (29 may) → resultado determinista."""
    d.now_for = lambda tz=None: _NOW
    at.generate = AsyncMock(side_effect=gen_side_effect)
    d.cl_repo.safe_insert = AsyncMock(side_effect=lambda label, fn, *a, **k: insert_mock(*a, **k))
    return asyncio.run(at.run_tool_loop("aria_2", "sys", [{"role": "user", "content": "x"}], client_id))


def test_no_tool_use_is_plain_conversation():
    captured = MagicMock(return_value="cid")
    text, err = _run("client-A", [(_resp(text="hola"), None)], captured)
    assert err is None and text == "hola"
    captured.assert_not_called()  # sin tool_use → NO crea draft (idéntico a hoy)


def test_tool_use_creates_supervised_draft():
    captured = {}
    def _insert(client_id, payload):
        captured["client_id"] = client_id; captured["payload"] = payload
        return "new-cid"
    block = _tool_block({"texto": "Post de prueba", "fecha_sugerida": "2026-06-01T15:00"})
    text, err = _run("client-A",
                     [(_resp(tool_calls=[block]), None), (_resp(text="lo dejé en Supervisado"), None)],
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
    _run("client-A", [(_resp(tool_calls=[block]), None), (_resp(text="ok"), None)], _insert)
    assert captured["client_id"] == "client-A"  # SESIÓN · nunca B (anti-G5 demostrado)


def test_second_generate_gets_antihype_addendum():
    """P1: el 2º generate recibe la regla anti-hype en su system (narración honesta)."""
    d.now_for = lambda tz=None: _NOW
    d.cl_repo.safe_insert = AsyncMock(return_value="cid")
    systems = []
    async def _gen(agent_code, system, messages, max_tokens=1024, tools=None):
        systems.append(system)
        return (_resp(tool_calls=[_tool_block({"texto": "x"})]) if tools else _resp(text="ok")), None
    at.generate = _gen
    asyncio.run(at.run_tool_loop("aria_2", "BASE", [{"role": "user", "content": "x"}], "client-A"))
    assert "sale volando" in systems[1] and "requiere su aprobación" in systems[1].lower()
