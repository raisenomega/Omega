"""zernio_facebook · adapter page-selection FB · httpx FAKE (G9 exime tests): parseo paginas+accountId · ZernioPublishError honesto (non-2xx/transporte/sin-id) · lista vacia != error (P1) · X-Connect-Token · tokens nunca en logs."""
import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from app.bc_cognition.infrastructure import zernio_facebook as zfb
from app.bc_cognition.infrastructure import zernio_adapter as za

ERR = za.ZernioPublishError


class _Resp:
    def __init__(self, status, payload):
        self.status_code, self._p, self.text = status, payload, json.dumps(payload)
    def json(self):
        return self._p


class _FakeClient:
    last: dict = {}
    def __init__(self, resp=None, boom=False):
        self._resp, self._boom = resp, boom
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return False
    async def get(self, url, params=None):
        _FakeClient.last = {"params": params}
        if self._boom: raise httpx.ConnectError("boom")
        return self._resp
    async def post(self, url, json=None):
        _FakeClient.last = {"json": json}
        if self._boom: raise httpx.ConnectError("boom")
        return self._resp


def _patch(monkeypatch, resp=None, boom=False, key="sk_test", cap=None):
    monkeypatch.setattr(za, "get_zernio_settings",
                        lambda: SimpleNamespace(zernio_api_key=key, zernio_api_base="https://zernio.com/api/v1"))
    def _mk(**kw):
        if cap is not None: cap.update(kw.get("headers", {}))
        return _FakeClient(resp, boom)
    monkeypatch.setattr(zfb.httpx, "AsyncClient", _mk)


def _run(c):
    return asyncio.run(c)


def test_get_pages_ok_y_session_param(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"pages": [{"id": "p1", "name": "La Casita"}]}))
    assert _run(zfb.get_facebook_pages("tt", "ct")) == [{"id": "p1", "name": "La Casita"}]
    assert _FakeClient.last["params"] == {"accountId": "tt"}   # wiring centralizado


def test_get_pages_vacia_NO_es_error(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"pages": []}))
    assert _run(zfb.get_facebook_pages("tt", "ct")) == []   # 0 paginas reales, NO raise


def test_get_pages_non2xx_levanta(monkeypatch):
    _patch(monkeypatch, _Resp(400, {"error": "bad"}))
    with pytest.raises(ERR): _run(zfb.get_facebook_pages("tt", "ct"))


def test_get_pages_transporte_levanta(monkeypatch):
    _patch(monkeypatch, boom=True)
    with pytest.raises(ERR): _run(zfb.get_facebook_pages("tt", "ct"))


def test_connect_token_va_en_header(monkeypatch):
    cap: dict = {}
    _patch(monkeypatch, _Resp(200, {"pages": []}), cap=cap)
    _run(zfb.get_facebook_pages("tt", "ct_secret"))
    assert cap.get("X-Connect-Token") == "ct_secret"


def test_select_ok_devuelve_account_id(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"_id": "acc_fb1", "pageId": "p1"}))
    assert _run(zfb.select_facebook_page("tt", "ct", "p1")) == "acc_fb1"
    assert _FakeClient.last["json"] == {"accountId": "tt", "pageId": "p1"}


def test_select_sin_id_levanta(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"platform": "facebook"}))
    with pytest.raises(ERR): _run(zfb.select_facebook_page("tt", "ct", "p1"))


def test_select_non2xx_levanta(monkeypatch):
    _patch(monkeypatch, _Resp(422, {"error": "x"}))
    with pytest.raises(ERR): _run(zfb.select_facebook_page("tt", "ct", "p1"))


def test_tokens_NO_se_loguean(monkeypatch, caplog):
    _patch(monkeypatch, boom=True)
    with pytest.raises(ERR): _run(zfb.get_facebook_pages("ttSECRET", "ctSECRET"))
    assert "ttSECRET" not in caplog.text and "ctSECRET" not in caplog.text   # solo presencia/len
