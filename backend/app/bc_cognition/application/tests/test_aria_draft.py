"""Tests de la creación del borrador supervisado (_aria_draft) + validación temporal → B2.
`now_for` mockeado al 29 may 2026 → deterministas. Cubre: futuro se conserva · pasada/basura → B2
(metadata sin fecha + mensaje 'agéndalo en el Calendario') · gates P2/P3. G9 exime tests."""
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

from app.bc_cognition.application import _aria_draft as d

_NOW = datetime(2026, 5, 29, 11, 0, tzinfo=ZoneInfo("America/Puerto_Rico"))


def _setup():
    """Mockea now (29 may) + captura el payload insertado."""
    d.now_for = lambda tz=None: _NOW
    captured = {}
    d.cl_repo.safe_insert = AsyncMock(
        side_effect=lambda label, fn, cid, payload: captured.setdefault("payload", payload) or "cid")
    return captured


def test_tool_result_is_honest_not_hype():
    """P1: dice 'pendiente aprobación' · NUNCA 'automátic/publica/volando'."""
    _setup()
    out = asyncio.run(d.execute_prepare_draft("client-A", {"texto": "post", "fecha_sugerida": "2026-06-01"}))
    msg = out["mensaje"].lower()
    assert "pendiente de aprobación" in msg and "sugerida" in msg
    assert "automátic" not in msg and "sale volando" not in msg and "se publicará hasta" in msg


def test_fecha_futura_se_conserva():
    cap = _setup()
    asyncio.run(d.execute_prepare_draft("client-A", {"texto": "p", "fecha_sugerida": "2026-06-01T15:00"}))
    assert cap["payload"]["metadata"]["fecha_sugerida"] == "2026-06-01T15:00"  # futuro válido


def test_fecha_pasada_cae_a_b2():
    cap = _setup()
    out = asyncio.run(d.execute_prepare_draft("client-A", {"texto": "p", "fecha_sugerida": "2020-01-01T10:00"}))
    assert cap["payload"]["metadata"]["fecha_sugerida"] is None  # pasada → descartada
    msg = out["mensaje"].lower()
    assert "sugerida" not in msg and "calendario" in msg  # B2: agéndalo tú en el Calendario


def test_iso_basura_cae_a_b2():
    cap = _setup()
    asyncio.run(d.execute_prepare_draft("client-A", {"texto": "p", "fecha_sugerida": "el martes"}))
    assert cap["payload"]["metadata"]["fecha_sugerida"] is None  # no parsea → B2


def test_low_confidence_blocks_p3(monkeypatch):
    cap = _setup()
    monkeypatch.setattr(d, "_DRAFT_CONFIDENCE", 5)  # < MIN_CONFIDENCE_TO_ACT (7)
    out = asyncio.run(d.execute_prepare_draft("client-A", {"texto": "algo"}))
    assert out["ok"] is False and "payload" not in cap  # should_enqueue False → NO inserta


def test_crisis_agent_never_enqueues_p2(monkeypatch):
    cap = _setup()
    monkeypatch.setattr(d, "_AGENT_CODE", "crisis_manager")  # P2: prohibido en flujo auto
    out = asyncio.run(d.execute_prepare_draft("client-A", {"texto": "algo"}))
    assert out["ok"] is False and "payload" not in cap
