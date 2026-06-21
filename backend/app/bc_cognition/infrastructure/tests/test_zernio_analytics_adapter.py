"""zernio_analytics_adapter · FAIL-SAFE honesto (httpx FAKE · NO red real · G9 exime tests).

Regla GLOBAL cero-sintéticos: ante CUALQUIER fallo de Zernio (non-2xx · timeout · transporte · sin key)
el adapter devuelve {} (o [] en list_accounts) · NUNCA un número inventado. Un panel vacío es honesto.
"""
import asyncio
from types import SimpleNamespace

import httpx

from app.bc_cognition.infrastructure import zernio_analytics_adapter as za


def _settings(key="sk_test"):
    return SimpleNamespace(zernio_api_key=key, zernio_api_base="https://zernio.com/api/v1")


class _Resp:
    def __init__(self, status, payload):
        self.status_code, self._p = status, payload

    def json(self):
        return self._p


class _FakeClient:
    def __init__(self, resp=None, raise_transport=False):
        self._resp, self._raise = resp, raise_transport

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def get(self, url, params=None):
        if self._raise:
            raise httpx.ConnectError("boom")
        return self._resp


def _patch(monkeypatch, resp=None, raise_transport=False, key="sk_test"):
    monkeypatch.setattr(za, "get_zernio_settings", lambda: _settings(key))
    monkeypatch.setattr(za.httpx, "AsyncClient", lambda **kw: _FakeClient(resp, raise_transport))


def test_list_accounts_envoltura_dict(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"accounts": [{"_id": "a1", "followersCount": 2}]}))
    assert asyncio.run(za.list_accounts()) == [{"_id": "a1", "followersCount": 2}]


def test_list_accounts_lista_directa(monkeypatch):
    _patch(monkeypatch, _Resp(200, [{"_id": "a1"}]))
    assert asyncio.run(za.list_accounts()) == [{"_id": "a1"}]


def test_list_accounts_non_2xx_vacio(monkeypatch):
    _patch(monkeypatch, _Resp(500, {"error": "boom"}))
    assert asyncio.run(za.list_accounts()) == []


def test_daily_metrics_200(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"dailyData": [{"postCount": 3}]}))
    assert asyncio.run(za.daily_metrics("p")) == {"dailyData": [{"postCount": 3}]}


def test_daily_metrics_404_vacio(monkeypatch):
    _patch(monkeypatch, _Resp(404, {"error": "x"}))
    assert asyncio.run(za.daily_metrics("p")) == {}


def test_best_time_timeout_vacio(monkeypatch):
    _patch(monkeypatch, raise_transport=True)
    assert asyncio.run(za.best_time("p")) == {}


def test_follower_history_transporte_vacio(monkeypatch):
    _patch(monkeypatch, raise_transport=True)
    assert asyncio.run(za.follower_history("a")) == {}


def test_sin_key_todo_vacio(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"dailyData": []}), key="")
    assert asyncio.run(za.list_accounts()) == []
    assert asyncio.run(za.daily_metrics("p")) == {}
