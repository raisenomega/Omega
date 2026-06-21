"""zernio_analytics_adapter · FAIL-SAFE honesto (httpx FAKE · NO red real · G9 exime tests).

Corazón de la honestidad P1: ante CUALQUIER fallo de Zernio (non-2xx · timeout · transporte · sin key)
el adapter devuelve {} · NUNCA un número inventado. Un panel vacío es honesto; uno con métricas falsas no.
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


def test_200_parsea_dict(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"dailyData": [{"postCount": 3}]}))
    out = asyncio.run(za.daily_metrics("prof_1"))
    assert out == {"dailyData": [{"postCount": 3}]}


def test_non_2xx_devuelve_vacio_honesto(monkeypatch):
    # 404/500 → {} · el panel mostrará empty, NO ceros que parezcan datos reales.
    _patch(monkeypatch, _Resp(404, {"error": "not found"}))
    assert asyncio.run(za.best_time("prof_1")) == {}


def test_500_devuelve_vacio(monkeypatch):
    _patch(monkeypatch, _Resp(500, {"error": "boom"}))
    assert asyncio.run(za.daily_metrics("prof_1")) == {}


def test_transporte_devuelve_vacio_sin_levantar(monkeypatch):
    # timeout/conexión caída → {} · el endpoint NUNCA debe romper por Zernio.
    _patch(monkeypatch, raise_transport=True)
    assert asyncio.run(za.follower_history("acc_1")) == {}


def test_sin_key_devuelve_vacio(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"dailyData": []}), key="")
    assert asyncio.run(za.daily_metrics("prof_1")) == {}


def test_lista_se_envuelve_en_items(monkeypatch):
    _patch(monkeypatch, _Resp(200, [{"a": 1}]))
    assert asyncio.run(za.best_time("prof_1")) == {"items": [{"a": 1}]}


def test_insights_plataforma_desconocida_no_pega(monkeypatch):
    # plataforma sin path mapeado → {} sin tocar la red (cero fabricación).
    _patch(monkeypatch, _Resp(200, {"metrics": {}}))
    assert asyncio.run(za.insights("acc_1", "myspace")) == {}
