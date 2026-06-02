"""Mapeo Zernio per-negocio · F5/2b (G9 exime tests).
CRÍTICO: cada endpoint exige user_owns_client → 403 si ajeno. Auth + Supabase + Zernio mockeados."""
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
    def update(self, payload): self.store["update"] = payload; return self
    def insert(self, payload): self.store["insert"] = payload; return self
    def execute(self): return SimpleNamespace(data=self.store.get("existing", []))


def _patch_auth(monkeypatch, owns=True):
    async def _user(auth): return {"id": "u1"}
    monkeypatch.setattr(zm, "get_current_user", _user)
    monkeypatch.setattr(zm.reader, "get_client", lambda cid: {"id": cid, "user_id": "u1"})
    monkeypatch.setattr(zm, "user_owns_client", lambda uid, c: owns)


def _patch_sb(monkeypatch, store):
    monkeypatch.setattr(zm, "get_supabase_service",
                        lambda: SimpleNamespace(client=SimpleNamespace(table=lambda t: _FakeTable(store))))


# ── OWNERSHIP 403 · los 3 endpoints ──
def test_get_available_403_si_no_dueno(monkeypatch):
    _patch_auth(monkeypatch, owns=False)
    async def _la(): return []
    monkeypatch.setattr(zm, "list_accounts", _la)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zm.zernio_available_accounts("c1", None, "auth"))
    assert e.value.status_code == 403


def test_post_map_403_si_no_dueno(monkeypatch):
    _patch_auth(monkeypatch, owns=False)
    body = zm.ZernioMapRequest(zernio_account_id="Z1")
    with pytest.raises(HTTPException) as e:
        asyncio.run(zm.map_zernio_account("c1", "instagram", body, "auth"))
    assert e.value.status_code == 403


def test_delete_unmap_403_si_no_dueno(monkeypatch):
    _patch_auth(monkeypatch, owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zm.unmap_zernio_account("c1", "instagram", "auth"))
    assert e.value.status_code == 403


# ── Happy paths ──
def test_get_available_filtra_platform(monkeypatch):
    _patch_auth(monkeypatch, owns=True)
    async def _la(): return [{"_id": "ig1", "platform": "instagram", "name": "@a"},
                             {"_id": "fb1", "platform": "facebook", "name": "@b"}]
    monkeypatch.setattr(zm, "list_accounts", _la)
    out = asyncio.run(zm.zernio_available_accounts("c1", "instagram", "auth"))
    assert out.total == 1 and out.items[0].zernio_account_id == "ig1"


def test_post_map_inserta_si_no_existe(monkeypatch):
    _patch_auth(monkeypatch, owns=True)
    store = {"existing": []}
    _patch_sb(monkeypatch, store)
    body = zm.ZernioMapRequest(zernio_account_id="Z1", zernio_account_handle="@acme")
    out = asyncio.run(zm.map_zernio_account("c1", "instagram", body, "auth"))
    assert out["ok"] is True and store["insert"]["zernio_account_id"] == "Z1"


def test_post_map_updatea_si_existe(monkeypatch):
    _patch_auth(monkeypatch, owns=True)
    store = {"existing": [{"id": "row1"}]}
    _patch_sb(monkeypatch, store)
    body = zm.ZernioMapRequest(zernio_account_id="Z2")
    asyncio.run(zm.map_zernio_account("c1", "instagram", body, "auth"))
    assert store["update"]["zernio_account_id"] == "Z2"


def test_delete_unmap_nullea_el_mapeo(monkeypatch):
    _patch_auth(monkeypatch, owns=True)
    store = {"existing": []}
    _patch_sb(monkeypatch, store)
    asyncio.run(zm.unmap_zernio_account("c1", "instagram", "auth"))
    assert store["update"]["zernio_account_id"] is None
