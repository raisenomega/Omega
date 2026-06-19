"""B-2 FB · endpoints page-picker (pending/select · JWT): lista {id,name} · 409 sin pending/profile/otro-user · select persiste+clear · profileId+userProfile propagados · userProfile None→409 honesto (no crash) · 422→clear (finally). G9 exime tests."""
import asyncio
import pytest
from fastapi import HTTPException

from app.api.routes.clients_v3.handlers import zernio_oauth as zo
from app.api.routes.clients_v3.handlers import zernio_fb_pages as fb
from app.api.routes.clients_v3.handlers import _zernio_pending as pend

CID = "client-A"
_REQ = fb.SelectPageRequest(page_id="pg1")


def _auth(monkeypatch, owns=True):
    async def _u(a):
        return {"id": "u1"}
    monkeypatch.setattr(zo, "get_current_user", _u)
    monkeypatch.setattr(zo.reader, "get_client", lambda cid: {"id": cid, "user_id": "u1", "zernio_profile_id": "P"})
    monkeypatch.setattr(zo, "user_owns_client", lambda u, c: owns)
    pend._store.clear()


def _run(c):
    return asyncio.run(c)


def _exc(c) -> HTTPException:
    with pytest.raises(HTTPException) as e:
        _run(c)
    return e.value


def test_pending_pages_lista_solo_id_name(monkeypatch):
    _auth(monkeypatch)
    pend.stash_pending("u1", CID, "facebook", "tt", "ct")
    seen: dict = {}
    async def _pages(tt, ct, pid):
        seen["pid"] = pid
        return [{"id": "pg1", "name": "La Casita", "secret": "x"}]
    monkeypatch.setattr(fb, "get_facebook_pages", _pages)
    assert _run(fb.fb_pending_pages(CID, "auth")) == {"pages": [{"id": "pg1", "name": "La Casita"}]}
    assert seen["pid"] == "P"   # profileId del negocio propagado a Zernio (fix 400 'Profile ID is required')


def test_pending_pages_sin_profile_409(monkeypatch):
    _auth(monkeypatch)
    monkeypatch.setattr(zo.reader, "get_client", lambda cid: {"id": cid, "user_id": "u1"})  # sin zernio_profile_id
    pend.stash_pending("u1", CID, "facebook", "tt", "ct")
    assert _exc(fb.fb_pending_pages(CID, "auth")).status_code == 409


def test_pending_pages_sin_pending_409(monkeypatch):
    _auth(monkeypatch)
    assert _exc(fb.fb_pending_pages(CID, "auth")).status_code == 409


def test_pending_pages_otro_user_no_recupera(monkeypatch):
    _auth(monkeypatch)   # stash de OTRO user (u2) · JWT u1 → key no matchea → 409 (no entrega tokens · defensa)
    pend.stash_pending("u2", CID, "facebook", "tt", "ct")
    assert _exc(fb.fb_pending_pages(CID, "auth")).status_code == 409


def test_select_page_ok_persiste_y_limpia(monkeypatch):
    _auth(monkeypatch)
    pend.stash_pending("u1", CID, "facebook", "tt", "ct", {"id": "u9"})
    async def _sel(tt, ct, page, prof, up):
        assert prof == "P" and up == {"id": "u9"}   # profileId + userProfile propagados al select
        return "acc_fb1"
    async def _persist(c, p, prof, account_id=None):
        return {"zernio_account_id": account_id, "handle": "h"}
    monkeypatch.setattr(fb, "select_facebook_page", _sel)
    monkeypatch.setattr(fb, "persist_zernio_account", _persist)
    out = _run(fb.fb_select_page(CID, _REQ, "auth"))
    assert out["ok"] is True and out["zernio_account_id"] == "acc_fb1"
    assert pend.get_pending("u1", CID, "facebook") is None   # clear tras éxito


def test_select_page_sin_pending_409(monkeypatch):
    _auth(monkeypatch)
    assert _exc(fb.fb_select_page(CID, _REQ, "auth")).status_code == 409


def test_select_page_sin_userprofile_409(monkeypatch):
    _auth(monkeypatch)   # stash SIN userProfile (None · callback degradó) → el POST select lo exige → 409, NO crash
    pend.stash_pending("u1", CID, "facebook", "tt", "ct")
    err = _exc(fb.fb_select_page(CID, _REQ, "auth"))
    assert err.status_code == 409 and "userprofile" in err.detail


def test_select_page_persist_422_limpia_igual(monkeypatch):
    _auth(monkeypatch)
    pend.stash_pending("u1", CID, "facebook", "tt", "ct", {"id": "u9"})
    async def _sel(tt, ct, page, prof, up):
        return "acc_fb1"
    async def _persist(*a, **k):
        raise HTTPException(status_code=422, detail="zernio_account_not_in_profile")
    monkeypatch.setattr(fb, "select_facebook_page", _sel)
    monkeypatch.setattr(fb, "persist_zernio_account", _persist)
    assert _exc(fb.fb_select_page(CID, _REQ, "auth")).status_code == 422
    assert pend.get_pending("u1", CID, "facebook") is None   # clear en finally aunque falle
