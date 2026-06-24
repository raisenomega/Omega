"""Commit 3 (Vía A) · GET /oauth/google/properties + POST /oauth/google/property.
Ownership real (resolve_client_or_403 · 403 ajeno) + persistencia del property_id elegido en
external_account_id (UPDATE, NO store_token) + 400 vacío + 404 sin fila (no conectado)."""
import asyncio
import importlib

import pytest
from fastapi import HTTPException

import app.api.routes.content_lab_v3._client_resolver as cr

gg = importlib.import_module("app.api.routes.oauth.handlers.google_ga4")


def _auth(monkeypatch, client, owns=True):
    async def _user(a):
        return {"id": "u1"}
    monkeypatch.setattr(gg, "get_current_user", _user)
    monkeypatch.setattr(cr.clients_reader, "get_client", lambda cid: client)
    monkeypatch.setattr(cr, "user_owns_client", lambda uid, c: owns)


def test_properties_negocio_ajeno_403(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u2"}, owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(gg.google_properties(client_id="c1", authorization="auth"))
    assert e.value.status_code == 403


def test_properties_propio_lista(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1"})
    async def _list(cid):
        return [{"property_id": "539450994", "display_name": "Omega Raisen"}]
    monkeypatch.setattr(gg, "list_ga4_properties", _list)
    out = asyncio.run(gg.google_properties(client_id="c1", authorization="auth"))
    assert out["properties"][0]["property_id"] == "539450994"


def test_property_negocio_ajeno_403(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u2"}, owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(gg.set_google_property(gg.PropertyBody(property_id="539450994"), client_id="c1", authorization="auth"))
    assert e.value.status_code == 403


def test_property_persiste_external_account_id(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1"})
    captured = {}
    async def _set(cid, provider, pid):
        captured.update(cid=cid, provider=provider, pid=pid)
        return 1
    monkeypatch.setattr(gg, "set_external_account_id", _set)
    out = asyncio.run(gg.set_google_property(gg.PropertyBody(property_id=" 539450994 "), client_id="c1", authorization="auth"))
    assert captured == {"cid": "c1", "provider": "google", "pid": "539450994"}  # trim aplicado
    assert out == {"ok": True, "property_id": "539450994"}


def test_property_vacio_400(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1"})
    with pytest.raises(HTTPException) as e:
        asyncio.run(gg.set_google_property(gg.PropertyBody(property_id="   "), client_id="c1", authorization="auth"))
    assert e.value.status_code == 400


def test_property_sin_fila_404(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1"})
    async def _set(cid, provider, pid):
        return 0  # ninguna fila (no conectado)
    monkeypatch.setattr(gg, "set_external_account_id", _set)
    with pytest.raises(HTTPException) as e:
        asyncio.run(gg.set_google_property(gg.PropertyBody(property_id="539450994"), client_id="c1", authorization="auth"))
    assert e.value.status_code == 404
