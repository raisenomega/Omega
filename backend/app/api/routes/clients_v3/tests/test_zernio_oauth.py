"""B-2 · ensure-profile / connect-url / connected-accounts · ownership + reuso de profile (G9 exime tests)."""
import asyncio
import importlib

import pytest
from fastapi import HTTPException

zo = importlib.import_module("app.api.routes.clients_v3.handlers.zernio_oauth")


def _auth(monkeypatch, client, owns=True):
    async def _user(a): return {"id": "u1"}
    monkeypatch.setattr(zo, "get_current_user", _user)
    monkeypatch.setattr(zo.reader, "get_client", lambda cid: client)
    monkeypatch.setattr(zo, "user_owns_client", lambda uid, c: owns)


def test_ensure_profile_403_si_no_dueno(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u2"}, owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zo.ensure_zernio_profile("c1", "auth"))
    assert e.value.status_code == 403


def test_ensure_profile_crea_si_falta_y_guarda(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "name": "Zafacones", "zernio_profile_id": None})
    saved = {}
    async def _create(name, description=""): return "prof_new"
    monkeypatch.setattr(zo, "create_profile", _create)
    monkeypatch.setattr(zo.repo, "update_client_by_id", lambda cid, f: saved.update(f) or 1)
    out = asyncio.run(zo.ensure_zernio_profile("c1", "auth"))
    assert out["zernio_profile_id"] == "prof_new" and saved["zernio_profile_id"] == "prof_new"


def test_ensure_profile_reusa_si_existe(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    called = {"create": False}
    async def _create(name, description=""): called["create"] = True; return "X"
    monkeypatch.setattr(zo, "create_profile", _create)
    out = asyncio.run(zo.ensure_zernio_profile("c1", "auth"))
    assert out["zernio_profile_id"] == "prof_ya" and called["create"] is False   # NO recrea


def test_connect_url_devuelve_auth_url(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    async def _cu(platform, pid): return f"https://www.facebook.com/oauth?profileId={pid}"
    monkeypatch.setattr(zo, "get_connect_url", _cu)
    out = asyncio.run(zo.zernio_connect_url("c1", "facebook", "auth"))
    assert "facebook.com" in out["auth_url"] and "prof_ya" in out["auth_url"]


def test_connected_accounts_lista_del_profile(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    async def _la(pid): return [{"_id": "ig1", "platform": "instagram", "username": "@z"}]
    monkeypatch.setattr(zo, "list_accounts", _la)
    out = asyncio.run(zo.zernio_connected_accounts("c1", "auth"))
    assert out["profile"] == "prof_ya" and out["items"][0]["zernio_account_id"] == "ig1"
