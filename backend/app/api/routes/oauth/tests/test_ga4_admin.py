"""Commit 3 · list_ga4_properties parsea el contrato OFICIAL de accountSummaries.list:
accountSummaries[].propertySummaries[].property = "properties/<id>" → {property_id, display_name}.
Best-effort honesto: sin token → [] · non-200 → []."""
import asyncio
import importlib

ga = importlib.import_module("app.api.routes.oauth._ga4_admin")


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self.text = ""
        self._p = payload

    def json(self):
        return self._p


class _Client:
    def __init__(self, resp):
        self._resp = resp

    def __call__(self, *a, **k):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def get(self, *a, **k):
        return self._resp


_OK = {"accountSummaries": [
    {"displayName": "Acc", "propertySummaries": [
        {"property": "properties/1000", "displayName": "Mi Sitio"}]}]}


def test_parsea_property_id_del_formato_oficial(monkeypatch):
    async def _tok(cid, prov):
        return {"access_token": "tok"}
    monkeypatch.setattr(ga, "get_token", _tok)
    monkeypatch.setattr(ga.httpx, "AsyncClient", _Client(_Resp(200, _OK)))
    out = asyncio.run(ga.list_ga4_properties("c1"))
    assert out == [{"property_id": "1000", "display_name": "Mi Sitio"}]  # strip "properties/"


def test_sin_token_vacio(monkeypatch):
    async def _tok(cid, prov):
        return None
    monkeypatch.setattr(ga, "get_token", _tok)
    assert asyncio.run(ga.list_ga4_properties("c1")) == []


def test_non_200_vacio(monkeypatch):
    async def _tok(cid, prov):
        return {"access_token": "tok"}
    monkeypatch.setattr(ga, "get_token", _tok)
    monkeypatch.setattr(ga.httpx, "AsyncClient", _Client(_Resp(403, {})))
    assert asyncio.run(ga.list_ga4_properties("c1")) == []
