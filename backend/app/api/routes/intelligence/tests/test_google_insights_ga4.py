"""Commit 3 · cierra el lazo: con external_account_id (property_id) presente, _google_insights SÍ
consulta GA4 (antes lo saltaba por 'if property_id:'). Sin él, lo salta (honesto)."""
import asyncio
import importlib

gi = importlib.import_module("app.api.routes.intelligence._google_insights")


class _Resp:
    status_code = 200
    text = ""

    def json(self):
        return {"rows": [{"metricValues": [{"value": "7"}]}]}  # GA4 runReport → 7 sessions


class _Client:
    def __init__(self, *a, **k):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, *a, **k):
        return _Resp()


def test_ga4_se_consulta_con_property_id(monkeypatch):
    async def _get_token(cid, provider):
        return {"access_token": "tok", "external_account_id": "539450994"}
    monkeypatch.setattr(gi, "get_token", _get_token)
    monkeypatch.setattr(gi.httpx, "AsyncClient", _Client)
    out = asyncio.run(gi.fetch_google_insights("c1", None))   # site_url None → solo GA4
    assert out["state"] == "ok" and out["metrics"]["sessions"] == 7


def test_ga4_se_salta_sin_property_id(monkeypatch):
    async def _get_token(cid, provider):
        return {"access_token": "tok"}  # sin external_account_id → property_id None
    monkeypatch.setattr(gi, "get_token", _get_token)
    monkeypatch.setattr(gi.httpx, "AsyncClient", _Client)
    out = asyncio.run(gi.fetch_google_insights("c1", None))
    assert out["state"] == "empty"   # GA4 saltado + sin site_url → sin métricas (honesto)
