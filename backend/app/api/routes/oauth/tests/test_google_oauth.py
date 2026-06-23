"""Fase A · /oauth/google authorize+status toman el client_id del Switcher + ownership real.
Corazón del DEBT-ANALYTICS-OAUTH-PER-CLIENT: un reseller NO autoriza/consulta Google de un negocio
ajeno. Ownership = resolve_client_or_403 verbatim (get_client + user_owns_client · igual que chips)."""
import asyncio
import importlib
from urllib.parse import urlparse, parse_qs

import pytest
from fastapi import HTTPException

import app.api.routes.content_lab_v3._client_resolver as cr

go = importlib.import_module("app.api.routes.oauth.handlers.google_oauth")


def _auth(monkeypatch, client, owns=True):
    """JWT + ownership REAL (deps de resolve_client_or_403) -> ejercita el 403/404 de verdad."""
    async def _user(a):
        return {"id": "u1"}
    monkeypatch.setattr(go, "get_current_user", _user)
    monkeypatch.setattr(cr.clients_reader, "get_client", lambda cid: client)
    monkeypatch.setattr(cr, "user_owns_client", lambda uid, c: owns)


def _creds(monkeypatch):
    """Credenciales de app + clave HMAC presentes -> authorize llega a firmar el state."""
    monkeypatch.setattr(go, "_require_google_creds", lambda: ("app-id", "app-secret"))
    monkeypatch.setattr(go, "_signing_key", lambda: b"test-hmac-key")


def test_authorize_propio_firma_ese_client_id(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1"})
    _creds(monkeypatch)
    out = asyncio.run(go.google_authorize(client_id="c1", authorization="auth"))
    state = parse_qs(urlparse(out["authorize_url"]).query)["state"][0]
    assert go._verify_state(state) == "c1"      # el state firma EL negocio del Switcher


def test_authorize_negocio_ajeno_403(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u2"}, owns=False)
    _creds(monkeypatch)
    with pytest.raises(HTTPException) as e:
        asyncio.run(go.google_authorize(client_id="c1", authorization="auth"))
    assert e.value.status_code == 403           # CORAZON DEL DEBT (aislamiento)


def test_authorize_client_inexistente_404(monkeypatch):
    _auth(monkeypatch, None)
    _creds(monkeypatch)
    with pytest.raises(HTTPException) as e:
        asyncio.run(go.google_authorize(client_id="cX", authorization="auth"))
    assert e.value.status_code == 404


def test_status_propio_usa_ese_client_id(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1"})
    captured = {}

    async def _get_token(cid, provider):
        captured["cid"] = cid
        return {"scopes": "analytics", "refresh_token": "r"}

    monkeypatch.setattr(go, "get_token", _get_token)
    out = asyncio.run(go.google_status(client_id="c1", authorization="auth"))
    assert captured["cid"] == "c1" and out["connected"] is True


def test_status_negocio_ajeno_403(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u2"}, owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(go.google_status(client_id="c1", authorization="auth"))
    assert e.value.status_code == 403
