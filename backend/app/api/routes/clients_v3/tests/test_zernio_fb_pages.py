"""B-2 FB · endpoints page-picker (pending-pages + select-page · JWT). Cubre: lista solo {id,name} ·
409 sin pending · DEFENSA otro user no recupera (key por user_id) · select persiste + clear · 409 sin
pending · persist 422 → clear igual (finally · no deja stash vivo). G9 exime tests."""
import asyncio
import pytest
from fastapi import HTTPException

from app.api.routes.clients_v3.handlers import zernio_oauth as zo
from app.api.routes.clients_v3.handlers import zernio_fb_pages as fb
from app.api.routes.clients_v3.handlers import _zernio_pending as pend

CID = "client-A"


def _auth(monkeypatch, owns=True):
    async def _u(a):
        return {"id": "u1"}
    monkeypatch.setattr(zo, "get_current_user", _u)
    monkeypatch.setattr(zo.reader, "get_client", lambda cid: {"id": cid, "user_id": "u1", "zernio_profile_id": "P"})
    monkeypatch.setattr(zo, "user_owns_client", lambda u, c: owns)
    pend._store.clear()


def _run(c):
    return asyncio.run(c)


def test_pending_pages_lista_solo_id_name(monkeypatch):
    _auth(monkeypatch)
    pend.stash_pending("u1", CID, "facebook", "tt", "ct")
    async def _pages(tt, ct):
        return [{"id": "pg1", "name": "La Casita", "secret": "x"}]
    monkeypatch.setattr(fb, "get_facebook_pages", _pages)
    assert _run(fb.fb_pending_pages(CID, "auth")) == {"pages": [{"id": "pg1", "name": "La Casita"}]}


def test_pending_pages_sin_pending_409(monkeypatch):
    _auth(monkeypatch)
    with pytest.raises(HTTPException) as e:
        _run(fb.fb_pending_pages(CID, "auth"))
    assert e.value.status_code == 409


def test_pending_pages_otro_user_no_recupera(monkeypatch):
    # el stash lo creó OTRO user (u2) · el JWT es u1 → key no matchea → 409 (no entrega tokens · defensa)
    _auth(monkeypatch)
    pend.stash_pending("u2", CID, "facebook", "tt", "ct")
    with pytest.raises(HTTPException) as e:
        _run(fb.fb_pending_pages(CID, "auth"))
    assert e.value.status_code == 409


def test_select_page_ok_persiste_y_limpia(monkeypatch):
    _auth(monkeypatch)
    pend.stash_pending("u1", CID, "facebook", "tt", "ct")
    async def _sel(tt, ct, pid):
        return "acc_fb1"
    async def _persist(c, p, prof, account_id=None):
        return {"zernio_account_id": account_id, "handle": "h"}
    monkeypatch.setattr(fb, "select_facebook_page", _sel)
    monkeypatch.setattr(fb, "persist_zernio_account", _persist)
    out = _run(fb.fb_select_page(CID, fb.SelectPageRequest(page_id="pg1"), "auth"))
    assert out["ok"] is True and out["zernio_account_id"] == "acc_fb1"
    assert pend.get_pending("u1", CID, "facebook") is None   # clear tras éxito


def test_select_page_sin_pending_409(monkeypatch):
    _auth(monkeypatch)
    with pytest.raises(HTTPException) as e:
        _run(fb.fb_select_page(CID, fb.SelectPageRequest(page_id="pg1"), "auth"))
    assert e.value.status_code == 409


def test_select_page_persist_422_limpia_igual(monkeypatch):
    _auth(monkeypatch)
    pend.stash_pending("u1", CID, "facebook", "tt", "ct")
    async def _sel(tt, ct, pid):
        return "acc_fb1"
    async def _persist(*a, **k):
        raise HTTPException(status_code=422, detail="zernio_account_not_in_profile")
    monkeypatch.setattr(fb, "select_facebook_page", _sel)
    monkeypatch.setattr(fb, "persist_zernio_account", _persist)
    with pytest.raises(HTTPException) as e:
        _run(fb.fb_select_page(CID, fb.SelectPageRequest(page_id="pg1"), "auth"))
    assert e.value.status_code == 422
    assert pend.get_pending("u1", CID, "facebook") is None   # clear en finally aunque falle
