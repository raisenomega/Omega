"""Test del toggle Modo Autónomo (REX) · gating por compra + aislamiento por negocio.

Encender SIN rex_addon_active → 403 · encender CON add-on → setea true · apagar siempre OK.
"""
import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

import app.api.routes.calendar_v3.handlers.autonomous_mode as am


class _FakeTable:
    def __init__(self, store: dict[str, Any]) -> None:
        self.store = store

    def update(self, p: dict[str, Any]) -> "_FakeTable":
        self.store["update"] = p
        return self

    def eq(self, *a: object) -> "_FakeTable":
        return self

    def execute(self) -> None:
        return None


def _setup(monkeypatch: pytest.MonkeyPatch, client: dict[str, Any]) -> dict[str, Any]:
    store: dict[str, Any] = {}

    async def _user(auth: object) -> dict[str, str]:
        return {"id": "u1"}
    monkeypatch.setattr(am, "get_current_user", _user)
    monkeypatch.setattr(am, "resolve_client_or_403", lambda uid, cid: client)
    monkeypatch.setattr(am, "get_supabase_service",
                        lambda: SimpleNamespace(client=SimpleNamespace(table=lambda t: _FakeTable(store))))
    return store


def test_enable_without_addon_403(monkeypatch: pytest.MonkeyPatch) -> None:
    _setup(monkeypatch, {"id": "c1", "rex_addon_active": False})
    req = am.AutonomousModeRequest(client_id="c1", enabled=True)
    with pytest.raises(HTTPException) as e:
        asyncio.run(am.set_autonomous_mode(req, "auth"))
    assert e.value.status_code == 403 and e.value.detail == "rex_addon_not_active"


def test_enable_with_addon_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _setup(monkeypatch, {"id": "c1", "rex_addon_active": True})
    req = am.AutonomousModeRequest(client_id="c1", enabled=True)
    out = asyncio.run(am.set_autonomous_mode(req, "auth"))
    assert out == {"autonomous_mode_on": True}
    assert store["update"] == {"autonomous_mode_on": True}


def test_disable_always_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    store = _setup(monkeypatch, {"id": "c1", "rex_addon_active": False})  # sin add-on
    req = am.AutonomousModeRequest(client_id="c1", enabled=False)         # apagar igual OK
    out = asyncio.run(am.set_autonomous_mode(req, "auth"))
    assert out == {"autonomous_mode_on": False}
    assert store["update"] == {"autonomous_mode_on": False}
