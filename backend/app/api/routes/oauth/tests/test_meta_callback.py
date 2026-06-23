"""Fase B3a · el callback de Meta redirige al relay /oauth/return (popup), NO a /settings.
Solo cambia el destino del RedirectResponse · la lógica de token y _verify_state quedan intactas.
provider=meta&status=connected en éxito · status=error si el exchange falla."""
import asyncio
import importlib

from fastapi import HTTPException

mo = importlib.import_module("app.api.routes.oauth.handlers.meta_oauth")


def _settings(monkeypatch):
    class _S:
        meta_app_id = "id"
        meta_app_secret = "sec"
        oauth_redirect_base = ""
    monkeypatch.setattr(mo, "get_oauth_settings", lambda: _S())
    monkeypatch.setattr(mo, "_verify_state", lambda s: "c1")


def test_callback_exito_redirige_al_relay(monkeypatch):
    _settings(monkeypatch)
    async def _ex(code):
        return {"access_token": "tok", "expires_in": 3600}
    async def _pg(t):
        return None
    async def _store(*a, **k):
        return None
    monkeypatch.setattr(mo, "_exchange_code", _ex)
    monkeypatch.setattr(mo, "_fetch_page_id", _pg)
    monkeypatch.setattr(mo, "store_token", _store)
    resp = asyncio.run(mo.meta_callback(code="x", state="st"))
    assert resp.status_code == 302
    assert "/oauth/return?provider=meta&status=connected" in resp.headers["location"]


def test_callback_error_redirige_al_relay(monkeypatch):
    _settings(monkeypatch)
    async def _ex(code):
        raise HTTPException(status_code=502, detail="meta_exchange_failed")
    monkeypatch.setattr(mo, "_exchange_code", _ex)
    resp = asyncio.run(mo.meta_callback(code="x", state="st"))
    assert "/oauth/return?provider=meta&status=error" in resp.headers["location"]
