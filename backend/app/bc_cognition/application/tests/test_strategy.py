"""Tests DEBT-096 F1: cadencia (domain puro) · parse_strategy · use_generate_strategy REUSA el
pipeline de ARIA (lo LLAMA, no lo duplica) y persiste. G9 exime tests."""
import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.bc_cognition.domain.strategy_cadence import cadence_for
from app.bc_cognition.domain.strategy_prompt import build_strategy_system, parse_strategy
from app.bc_cognition.application import use_generate_strategy as ugs


# ---------- domain puro ----------
def test_cadence_por_nivel():
    assert cadence_for(1) is None
    assert cadence_for(2) == "semanal"
    assert cadence_for(3) == "tres_semana"
    assert cadence_for(4) == "diaria"
    assert cadence_for(99) is None


def test_parse_strategy_json_valido():
    s = parse_strategy('{"titulo": "Plan X", "pilares": ["a"]}')
    assert s["titulo"] == "Plan X" and s["contenido"]["pilares"] == ["a"]


def test_parse_strategy_con_fence_y_texto_alrededor():
    s = parse_strategy('Acá va:\n```json\n{"titulo": "Y"}\n```\nlisto')
    assert s["titulo"] == "Y"


def test_parse_strategy_basura_es_none():
    assert parse_strategy("no hay json") is None
    assert parse_strategy('{"sin": "titulo"}') is None
    assert parse_strategy("") is None


def test_build_strategy_system_reusa_bloques():
    sysp = build_strategy_system("CTX", "WEB", "MEM")
    assert "CTX" in sysp and "WEB" in sysp and "MEM" in sysp and "JSON" in sysp


# ---------- use case · REUSA el pipeline (lo LLAMA) ----------
def test_use_generate_strategy_reusa_pipeline_y_persiste(monkeypatch):
    calls = {"web": 0, "ctx": 0}
    monkeypatch.setattr(ugs, "resolve_role", lambda sb, uid: ("client", "client-A", None, 3))
    monkeypatch.setattr(ugs, "get_supabase_service", lambda: MagicMock())

    def _fetch_ctx(sb, cid):
        calls["ctx"] += 1
        return {"niche": "limpieza"}
    monkeypatch.setattr(ugs.repo, "fetch_aria_context", _fetch_ctx)
    monkeypatch.setattr(ugs, "build_client_context_block", lambda ctx: "CTX_BLOCK")

    async def _web(*a, **k):
        calls["web"] += 1
        return "WEB_BLOCK"
    monkeypatch.setattr(ugs, "fetch_web_context", _web)
    monkeypatch.setattr(ugs, "load_and_format_memory", lambda *a, **k: "MEM_BLOCK")

    resp = MagicMock()
    resp.text = '{"titulo": "Estrategia semana 1", "pilares": ["x"]}'
    monkeypatch.setattr(ugs, "generate", AsyncMock(return_value=(resp, None)))

    captured = {}
    async def _safe_insert(label, fn, *args):
        captured["args"] = args
        return "new-strat-id"
    monkeypatch.setattr(ugs.repo, "safe_insert", _safe_insert)

    result, err = asyncio.run(ugs.use_generate_strategy("user-1"))
    assert err is None
    assert result.id == "new-strat-id" and result.titulo == "Estrategia semana 1"
    # reusó el pipeline (lo LLAMÓ, no lo duplicó):
    assert calls["ctx"] == 1 and calls["web"] == 1
    ugs.generate.assert_awaited_once()
    # persistió con el titulo parseado + tipo manual:
    assert "client-A" in captured["args"] and "Estrategia semana 1" in captured["args"] and "manual" in captured["args"]


def test_use_generate_strategy_sin_cliente_forbidden(monkeypatch):
    monkeypatch.setattr(ugs, "resolve_role", lambda sb, uid: ("reseller", None, "r1", 3))
    monkeypatch.setattr(ugs, "get_supabase_service", lambda: MagicMock())
    result, err = asyncio.run(ugs.use_generate_strategy("user-1"))
    assert result is None and err.code == "forbidden"


def test_use_generate_strategy_basura_no_persiste(monkeypatch):
    monkeypatch.setattr(ugs, "resolve_role", lambda sb, uid: ("client", "client-A", None, 3))
    monkeypatch.setattr(ugs, "get_supabase_service", lambda: MagicMock())
    monkeypatch.setattr(ugs.repo, "fetch_aria_context", lambda sb, cid: {"niche": "x"})
    monkeypatch.setattr(ugs, "build_client_context_block", lambda ctx: "CTX")
    monkeypatch.setattr(ugs, "fetch_web_context", AsyncMock(return_value=""))
    monkeypatch.setattr(ugs, "load_and_format_memory", lambda *a, **k: "")
    resp = MagicMock(); resp.text = "no es json"
    monkeypatch.setattr(ugs, "generate", AsyncMock(return_value=(resp, None)))
    inserted = {"n": 0}
    async def _si(*a, **k):
        inserted["n"] += 1; return "x"
    monkeypatch.setattr(ugs.repo, "safe_insert", _si)
    result, err = asyncio.run(ugs.use_generate_strategy("user-1"))
    assert result is None and err.code == "parse_error" and inserted["n"] == 0
