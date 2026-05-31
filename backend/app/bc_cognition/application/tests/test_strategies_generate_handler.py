"""Handler test · strategies/generate con client_id opcional (Switcher V1 · Commit 5).
Estilo monkeypatch + asyncio.run (igual que test_strategy.py · sin TestClient). G9 exime tests."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.routes.strategies_v1.handlers import generate as gen


def _ok_result():
    r = MagicMock(); r.id = "s1"; r.titulo = "T"; r.contenido = {}
    return r


def test_generate_con_client_id_usa_resolver(monkeypatch):
    monkeypatch.setattr(gen, "get_current_user", AsyncMock(return_value={"id": "user-1"}))
    monkeypatch.setattr(gen, "resolve_client_or_403", lambda uid, cid: {"id": cid})
    monkeypatch.setattr(gen, "check_budget", AsyncMock(return_value=True))
    captured = {}
    async def _ugs(client_id, reseller_id=None):
        captured["client_id"] = client_id
        return _ok_result(), None
    monkeypatch.setattr(gen, "use_generate_strategy", _ugs)
    out = asyncio.run(gen.generate_strategy(gen.GenerateStrategyRequest(client_id="biz-X"), "auth"))
    assert captured["client_id"] == "biz-X" and out["id"] == "s1"


def test_generate_sin_client_id_es_legacy(monkeypatch):
    monkeypatch.setattr(gen, "get_current_user", AsyncMock(return_value={"id": "user-1"}))
    monkeypatch.setattr(gen, "get_supabase_service", lambda: MagicMock())
    monkeypatch.setattr(gen, "resolve_role", lambda sb, uid: ("client", "own-client", None, 2))
    monkeypatch.setattr(gen, "check_budget", AsyncMock(return_value=True))
    captured = {}
    async def _ugs(client_id, reseller_id=None):
        captured["client_id"] = client_id
        return _ok_result(), None
    monkeypatch.setattr(gen, "use_generate_strategy", _ugs)
    out = asyncio.run(gen.generate_strategy(gen.GenerateStrategyRequest(), "auth"))
    assert captured["client_id"] == "own-client"


def test_generate_client_id_no_accesible_403(monkeypatch):
    monkeypatch.setattr(gen, "get_current_user", AsyncMock(return_value={"id": "user-1"}))
    def _deny(uid, cid):
        raise HTTPException(status_code=403, detail="client_access_denied")
    monkeypatch.setattr(gen, "resolve_client_or_403", _deny)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(gen.generate_strategy(gen.GenerateStrategyRequest(client_id="other"), "auth"))
    assert ei.value.status_code == 403
