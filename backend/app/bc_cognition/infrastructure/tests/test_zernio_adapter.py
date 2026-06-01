"""zernio_adapter · tests con httpx FAKE (NO red real · NO postea a Zernio · G9 exime tests).
Prueban LOGICA: parsea post_id · ZernioPublishError (4xx/sin-id/transporte) · ZernioNotConfigured sin key · publishNow vs scheduledFor. Todo fake (postear de verdad ensuciaria FB cada gate)."""
import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from app.bc_cognition.infrastructure import zernio_adapter as za

_PLAT = [{"platform": "facebook", "accountId": "a1"}]


def _settings(key="sk_test"):
    return SimpleNamespace(zernio_api_key=key, zernio_api_base="https://zernio.com/api/v1")


class _Resp:
    def __init__(self, status, payload):
        self.status_code, self._p, self.text = status, payload, json.dumps(payload)
    def json(self):
        return self._p


class _FakeClient:
    """Fake de httpx.AsyncClient · captura el body enviado, devuelve resp canned o levanta transporte."""
    last_body = None
    def __init__(self, resp=None, raise_transport=False):
        self._resp, self._raise = resp, raise_transport
    async def __aenter__(self):
        return self
    async def __aexit__(self, *a):
        return False
    async def post(self, url, json=None):
        _FakeClient.last_body = json
        if self._raise:
            raise httpx.ConnectError("boom")
        return self._resp
    async def get(self, url):
        if self._raise:
            raise httpx.ConnectError("boom")
        return self._resp


def _patch(monkeypatch, resp=None, raise_transport=False, key="sk_test"):
    monkeypatch.setattr(za, "get_zernio_settings", lambda: _settings(key))
    monkeypatch.setattr(za.httpx, "AsyncClient", lambda **kw: _FakeClient(resp, raise_transport))


def test_create_post_ok_devuelve_post_id(monkeypatch):
    _patch(monkeypatch, _Resp(201, {"post": {"_id": "post_abc"}}))
    out = asyncio.run(za.create_post("hola", _PLAT))
    assert out == "post_abc"
    assert _FakeClient.last_body["content"] == "hola"
    assert _FakeClient.last_body["platforms"] == _PLAT
    assert _FakeClient.last_body["publishNow"] is True  # sin scheduled_for → publishNow


def test_scheduled_usa_scheduledFor_no_publishNow(monkeypatch):
    _patch(monkeypatch, _Resp(201, {"post": {"_id": "p2"}}))
    asyncio.run(za.create_post("x", _PLAT, scheduled_for="2026-06-02T10:00:00"))
    assert _FakeClient.last_body.get("scheduledFor") == "2026-06-02T10:00:00"
    assert "publishNow" not in _FakeClient.last_body  # uno u otro


def test_media_va_como_mediaItems_url_type(monkeypatch):  # mediaItems:[{url,type}] no mediaUrls · type por ext
    _patch(monkeypatch, _Resp(201, {"post": {"_id": "p3"}}))
    asyncio.run(za.create_post("x", _PLAT, media_urls=["https://a/img.png", "https://a/v.mp4"]))
    assert _FakeClient.last_body["mediaItems"] == [{"url": "https://a/img.png", "type": "image"}, {"url": "https://a/v.mp4", "type": "video"}]
    assert "mediaUrls" not in _FakeClient.last_body


def test_4xx_levanta_honesto(monkeypatch):
    _patch(monkeypatch, _Resp(400, {"error": "bad request"}))
    with pytest.raises(za.ZernioPublishError):
        asyncio.run(za.create_post("x", _PLAT))


def test_sin_post_id_levanta(monkeypatch):
    _patch(monkeypatch, _Resp(201, {"post": {}}))
    with pytest.raises(za.ZernioPublishError):
        asyncio.run(za.create_post("x", _PLAT))


def test_transporte_levanta_publish_error(monkeypatch):
    _patch(monkeypatch, raise_transport=True)
    with pytest.raises(za.ZernioPublishError):
        asyncio.run(za.create_post("x", _PLAT))


def test_sin_key_levanta_not_configured(monkeypatch):
    _patch(monkeypatch, _Resp(201, {"post": {"_id": "x"}}), key="")
    with pytest.raises(za.ZernioNotConfigured):
        asyncio.run(za.create_post("x", _PLAT))


def test_list_accounts_ok(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"accounts": [{"_id": "a1", "platform": "facebook"}]}))
    assert asyncio.run(za.list_accounts()) == [{"_id": "a1", "platform": "facebook"}]
