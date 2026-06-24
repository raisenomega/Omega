"""Test del toggle Modo Autónomo (REX) · gating por compra + aislamiento por negocio.

Encender SIN rex_addon_active → 403 · encender CON add-on → setea true · apagar siempre OK.
"""
import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import HTTPException

import app.api.routes.calendar_v3.handlers.autonomous_mode as am
import app.bc_cognition.infrastructure.owner_accounts_repository as owners


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


def _setup(monkeypatch: pytest.MonkeyPatch, client: dict[str, Any],
           owner_ids: list[str] | None = None) -> dict[str, Any]:
    store: dict[str, Any] = {}

    async def _user(auth: object) -> dict[str, str]:
        return {"id": "u1"}
    monkeypatch.setattr(am, "get_current_user", _user)
    monkeypatch.setattr(am, "resolve_client_or_403", lambda uid, cid: client)
    monkeypatch.setattr(am, "get_supabase_service",
                        lambda: SimpleNamespace(client=SimpleNamespace(table=lambda t: _FakeTable(store))))
    monkeypatch.setattr(owners, "fetch_owner_user_ids", lambda: set(owner_ids or []))
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


def test_patch_owner_account_enable_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    # EL FIX A1.2: cuenta-dueño · columna False · efectivo True → encender PERMITIDO (200), no 403.
    store = _setup(monkeypatch, {"id": "c1", "user_id": "u-own", "rex_addon_active": False},
                   owner_ids=["u-own"])
    req = am.AutonomousModeRequest(client_id="c1", enabled=True)
    out = asyncio.run(am.set_autonomous_mode(req, "auth"))
    assert out == {"autonomous_mode_on": True}
    assert store["update"] == {"autonomous_mode_on": True}


def test_patch_normal_sin_addon_enable_403(monkeypatch: pytest.MonkeyPatch) -> None:
    # Cuenta normal (no dueña) sin add-on real → sigue 403 (no se rompió para los demás).
    _setup(monkeypatch, {"id": "c1", "user_id": "u-free", "rex_addon_active": False},
           owner_ids=["u-own"])
    req = am.AutonomousModeRequest(client_id="c1", enabled=True)
    with pytest.raises(HTTPException) as e:
        asyncio.run(am.set_autonomous_mode(req, "auth"))
    assert e.value.status_code == 403 and e.value.detail == "rex_addon_not_active"


def test_patch_aislamiento_cuenta_ajena_403(monkeypatch: pytest.MonkeyPatch) -> None:
    # La exención cambia el guard del add-on, NO el acceso: ownership sigue mandando.
    async def _user(auth: object) -> dict[str, str]:
        return {"id": "u1"}
    monkeypatch.setattr(am, "get_current_user", _user)

    def _deny(uid: str, cid: str) -> dict[str, Any]:
        raise HTTPException(status_code=403, detail="client_access_denied")
    monkeypatch.setattr(am, "resolve_client_or_403", _deny)
    req = am.AutonomousModeRequest(client_id="c1", enabled=True)
    with pytest.raises(HTTPException) as e:
        asyncio.run(am.set_autonomous_mode(req, "auth"))
    assert e.value.status_code == 403 and e.value.detail == "client_access_denied"


# ── GET autonomous-mode · rex_addon_active EFECTIVO (exención owner_accounts llega a la UI) ──

def _setup_get(monkeypatch: pytest.MonkeyPatch, client: dict[str, Any],
               owner_ids: list[str]) -> None:
    async def _user(auth: object) -> dict[str, str]:
        return {"id": "u1"}
    monkeypatch.setattr(am, "get_current_user", _user)
    monkeypatch.setattr(am, "resolve_client_or_403", lambda uid, cid: client)
    monkeypatch.setattr(owners, "fetch_owner_user_ids", lambda: set(owner_ids))


def test_get_owner_account_efectivo_true(monkeypatch: pytest.MonkeyPatch) -> None:
    # EL FIX: cuenta-dueño · columna False · efectivo True → el toggle se MUESTRA.
    # Mostrar ≠ encender: autonomous_mode_on sigue False (decisión del owner).
    _setup_get(monkeypatch, {"id": "c1", "user_id": "u-own",
                             "rex_addon_active": False, "autonomous_mode_on": False}, ["u-own"])
    out = asyncio.run(am.get_autonomous_mode("c1", "auth"))
    assert out["rex_addon_active"] is True
    assert out["autonomous_mode_on"] is False


def test_get_normal_account_sin_addon_false(monkeypatch: pytest.MonkeyPatch) -> None:
    # Cuenta normal sin add-on → sigue False (no se rompió para los demás).
    _setup_get(monkeypatch, {"id": "c1", "user_id": "u-free",
                             "rex_addon_active": False, "autonomous_mode_on": False}, ["u-own"])
    out = asyncio.run(am.get_autonomous_mode("c1", "auth"))
    assert out["rex_addon_active"] is False


def test_get_addon_real_en_columna_sigue_true(monkeypatch: pytest.MonkeyPatch) -> None:
    # Tipo Mail Boxes: add-on REAL en columna, no es dueño → sigue True (no se rompió).
    _setup_get(monkeypatch, {"id": "c1", "user_id": "u-free",
                             "rex_addon_active": True, "autonomous_mode_on": True}, ["u-own"])
    out = asyncio.run(am.get_autonomous_mode("c1", "auth"))
    assert out["rex_addon_active"] is True


def test_get_aislamiento_cuenta_ajena_403(monkeypatch: pytest.MonkeyPatch) -> None:
    # La exención cambia el VALOR, NO el acceso: ownership sigue validándose en resolve_client_or_403.
    async def _user(auth: object) -> dict[str, str]:
        return {"id": "u1"}
    monkeypatch.setattr(am, "get_current_user", _user)

    def _deny(uid: str, cid: str) -> dict[str, Any]:
        raise HTTPException(status_code=403, detail="client_access_denied")
    monkeypatch.setattr(am, "resolve_client_or_403", _deny)
    with pytest.raises(HTTPException) as e:
        asyncio.run(am.get_autonomous_mode("c1", "auth"))
    assert e.value.status_code == 403
