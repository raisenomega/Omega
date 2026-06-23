"""Fase B3a · el callback de Google redirige al relay /oauth/return (popup), NO a /settings.
Solo cambia el destino del RedirectResponse · la lógica de token y _verify_state quedan intactas.
provider=google&status=connected en éxito · status=error si el exchange falla."""
import asyncio
import importlib

go = importlib.import_module("app.api.routes.oauth.handlers.google_oauth")


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self.text = ""
        self._payload = payload

    def json(self):
        return self._payload


class _Client:  # async context manager mínimo que devuelve un _Resp fijo
    def __init__(self, resp):
        self._resp = resp

    def __call__(self, *a, **k):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, *a, **k):
        return self._resp


def _setup(monkeypatch, status_code):
    monkeypatch.setattr(go, "_verify_state", lambda s: "c1")
    monkeypatch.setattr(go, "_require_google_creds", lambda: ("id", "sec"))
    async def _store(*a, **k):
        return None
    monkeypatch.setattr(go, "store_token", _store)
    monkeypatch.setattr(go.httpx, "AsyncClient",
                        _Client(_Resp(status_code, {"access_token": "tok", "expires_in": 3600})))


def test_callback_exito_redirige_al_relay(monkeypatch):
    _setup(monkeypatch, 200)
    resp = asyncio.run(go.google_callback(code="x", state="st"))
    assert resp.status_code == 302
    assert "/oauth/return?provider=google&status=connected" in resp.headers["location"]


def test_callback_error_redirige_al_relay(monkeypatch):
    _setup(monkeypatch, 400)
    resp = asyncio.run(go.google_callback(code="x", state="st"))
    assert "/oauth/return?provider=google&status=error" in resp.headers["location"]
