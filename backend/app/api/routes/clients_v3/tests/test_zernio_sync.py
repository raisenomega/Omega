"""zernio-sync · captura del accountId conectado CON HARDENING anti-cross-publish (G9 exime tests).
Garantiza: ownership · handle autoritativo de Zernio (ignora body) · valida que el account pertenece
al profileId del negocio (no solo que el filtro lo trajo) · si no pertenece → 422, NO guarda."""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

zs = importlib.import_module("app.api.routes.clients_v3.handlers.zernio_sync")


class _FakeTable:
    def __init__(self, store): self.store = store
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def update(self, p): self.store["update"] = p; return self
    def insert(self, p): self.store["insert"] = p; return self
    def execute(self): return SimpleNamespace(data=self.store.get("existing", []))


def _setup(monkeypatch, accounts, client=None, owns=True, store=None):
    async def _user(a): return {"id": "u1"}
    monkeypatch.setattr(zs, "get_current_user", _user)
    monkeypatch.setattr(zs.reader, "get_client",
                        lambda cid: client if client is not None else {"id": cid, "user_id": "u1", "zernio_profile_id": "prof_zafa"})
    monkeypatch.setattr(zs, "user_owns_client", lambda uid, c: owns)
    async def _la(pid): return accounts
    monkeypatch.setattr(zs, "list_accounts", _la)
    if store is not None:
        monkeypatch.setattr(zs, "get_supabase_service",
                            lambda: SimpleNamespace(client=SimpleNamespace(table=lambda t: _FakeTable(store))))


def test_403_si_no_dueno(monkeypatch):
    _setup(monkeypatch, [], owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zs.zernio_sync("c1", "instagram", "auth"))
    assert e.value.status_code == 403


def test_409_si_negocio_sin_profile(monkeypatch):
    _setup(monkeypatch, [], client={"id": "c1", "user_id": "u1", "zernio_profile_id": None})
    with pytest.raises(HTTPException) as e:
        asyncio.run(zs.zernio_sync("c1", "instagram", "auth"))
    assert e.value.status_code == 409


def test_422_si_cuenta_no_pertenece_al_profile(monkeypatch):
    # la cuenta IG existe pero su profileId es de OTRO negocio → NO guardar (anti cross-publish)
    store = {"existing": []}
    _setup(monkeypatch, [{"_id": "ig1", "platform": "instagram",
                          "profileId": {"_id": "prof_OTRO"}, "username": "@otro"}], store=store)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zs.zernio_sync("c1", "instagram", "auth"))
    assert e.value.status_code == 422
    assert "insert" not in store and "update" not in store   # NO guardó nada


def test_ok_guarda_handle_autoritativo_de_zernio(monkeypatch):
    store = {"existing": []}
    _setup(monkeypatch, [{"_id": "ig_zafa", "platform": "instagram",
                          "profileId": {"_id": "prof_zafa"}, "username": "@zafaconesr"}], store=store)
    out = asyncio.run(zs.zernio_sync("c1", "instagram", "auth"))
    assert out["ok"] is True and out["zernio_account_id"] == "ig_zafa"
    assert store["insert"]["zernio_account_handle"] == "@zafaconesr"   # de Zernio, no de un body
    assert store["insert"]["zernio_account_id"] == "ig_zafa"
