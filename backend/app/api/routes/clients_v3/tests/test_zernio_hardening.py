"""Hardening anti-cross-publish del POST map (Parte A · auto-contenido).
El zernio_account_id se valida contra list_accounts() de Zernio server-side y el handle
guardado sale de Zernio, NO del body (no spoofeable). 422 si el id no existe / platform no cuadra."""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

zm = importlib.import_module("app.api.routes.clients_v3.handlers.zernio_mapping")


class _FakeTable:
    def __init__(self, store): self.store = store
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def update(self, p): self.store["update"] = p; return self
    def insert(self, p): self.store["insert"] = p; return self
    def execute(self): return SimpleNamespace(data=self.store.get("existing", []))


def _setup(monkeypatch, accounts, store=None):
    async def _user(auth): return {"id": "u1"}
    monkeypatch.setattr(zm, "get_current_user", _user)
    monkeypatch.setattr(zm.reader, "get_client", lambda cid: {"id": cid, "user_id": "u1"})
    monkeypatch.setattr(zm, "user_owns_client", lambda uid, c: True)
    async def _la(): return accounts
    monkeypatch.setattr(zm, "list_accounts", _la)
    if store is not None:
        monkeypatch.setattr(zm, "get_supabase_service",
                            lambda: SimpleNamespace(client=SimpleNamespace(table=lambda t: _FakeTable(store))))


def test_map_422_si_cuenta_inexistente(monkeypatch):
    _setup(monkeypatch, [{"_id": "OTRO", "platform": "instagram", "name": "@otro"}])
    with pytest.raises(HTTPException) as e:
        asyncio.run(zm.map_zernio_account("c1", "instagram", zm.ZernioMapRequest(zernio_account_id="NO_EXISTE"), "auth"))
    assert e.value.status_code == 422


def test_map_422_si_platform_no_coincide(monkeypatch):
    # el id existe pero es de otra red → 422 (anti binding cruzado de plataforma)
    _setup(monkeypatch, [{"_id": "Z1", "platform": "facebook", "name": "@fb"}])
    with pytest.raises(HTTPException) as e:
        asyncio.run(zm.map_zernio_account("c1", "instagram", zm.ZernioMapRequest(zernio_account_id="Z1"), "auth"))
    assert e.value.status_code == 422


def test_map_handle_autoritativo_ignora_body(monkeypatch):
    # body manda handle FALSO · debe guardarse el de Zernio (@from_zernio)
    store = {"existing": []}
    _setup(monkeypatch, [{"_id": "Z1", "platform": "instagram", "name": "@from_zernio"}], store)
    body = zm.ZernioMapRequest(zernio_account_id="Z1", zernio_account_handle="@spoofed")
    asyncio.run(zm.map_zernio_account("c1", "instagram", body, "auth"))
    assert store["insert"]["zernio_account_handle"] == "@from_zernio"
    assert store["insert"]["account_name"] == "@from_zernio"
