"""zernio_profiles · profiles + OAuth connect (B-2) · httpx FAKE (G9 exime tests · NO red real).
Contrato confirmado en vivo 17 jun: POST /profiles→{profile:{_id}} · GET /connect/<plat>?profileId→{authUrl}
· GET /accounts?profileId filtra."""
import asyncio
import importlib

import httpx
import pytest

za = importlib.import_module("app.bc_cognition.infrastructure.zernio_adapter")
zp = importlib.import_module("app.bc_cognition.infrastructure.zernio_profiles")


class _Resp:
    def __init__(self, code, data): self.status_code = code; self._d = data; self.text = str(data)
    def json(self): return self._d


class _Fake:
    last_url = None
    def __init__(self, resp): self._r = resp
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def post(self, url, json=None): _Fake.last_url = url; return self._r
    async def get(self, url): _Fake.last_url = url; return self._r


def _patch(monkeypatch, resp):
    monkeypatch.setattr(za, "get_zernio_settings",
                        lambda: type("S", (), {"zernio_api_key": "sk_test", "zernio_api_base": "https://zernio.com/api/v1"})())
    monkeypatch.setattr(zp.httpx, "AsyncClient", lambda **kw: _Fake(resp))
    monkeypatch.setattr(za.httpx, "AsyncClient", lambda **kw: _Fake(resp))


def test_create_profile_devuelve_id(monkeypatch):
    _patch(monkeypatch, _Resp(201, {"profile": {"_id": "prof_123"}}))
    assert asyncio.run(zp.create_profile("Zafacones Ramos")) == "prof_123"


def test_create_profile_sin_id_levanta(monkeypatch):
    _patch(monkeypatch, _Resp(201, {"profile": {}}))
    with pytest.raises(za.ZernioError):
        asyncio.run(zp.create_profile("X"))


def test_get_connect_url_authurl_profile_scoped(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"authUrl": "https://www.facebook.com/oauth?x=1"}))
    out = asyncio.run(zp.get_connect_url("facebook", "prof_123"))
    assert out == "https://www.facebook.com/oauth?x=1"
    assert "/connect/facebook" in _Fake.last_url and "profileId=prof_123" in _Fake.last_url


def test_get_connect_url_non2xx_levanta(monkeypatch):
    _patch(monkeypatch, _Resp(400, {"error": "bad"}))
    with pytest.raises(za.ZernioError):
        asyncio.run(zp.get_connect_url("facebook", "prof_123"))


def test_list_accounts_filtra_por_profile(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"accounts": [{"_id": "a1", "platform": "facebook"}]}))
    out = asyncio.run(za.list_accounts("prof_123"))
    assert out == [{"_id": "a1", "platform": "facebook"}]
    assert "profileId=prof_123" in _Fake.last_url


# ── B2.5 Capa B · find-by-name (exacto, seguro por el sufijo=PK) + get-or-create idempotente ──
def test_find_profile_by_name_exact_match(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"profiles": [
        {"name": "Otro", "_id": "p_otro"},
        {"name": "Zafacones Ramos · uuid1", "_id": "p_mio"},
    ]}))
    out = asyncio.run(zp.find_profile_by_name("Zafacones Ramos · uuid1"))
    assert out == "p_mio"


def test_find_profile_by_name_none_si_no_existe(monkeypatch):
    _patch(monkeypatch, _Resp(200, {"profiles": [{"name": "Otro", "_id": "p_otro"}]}))
    assert asyncio.run(zp.find_profile_by_name("No existe")) is None


def test_get_or_create_reusa_si_existe(monkeypatch):
    """Idempotencia: find encuentra el profile (mismo sufijo=suyo) -> reusa, NO crea (cierra huerfano)."""
    created = {"n": 0}
    async def _find(name): return "prof_existente"
    async def _create(name, description=""): created["n"] += 1; return "NUEVO"
    monkeypatch.setattr(zp, "find_profile_by_name", _find)
    monkeypatch.setattr(zp, "create_profile", _create)
    out = asyncio.run(zp.get_or_create_profile("X · uuid"))
    assert out == "prof_existente" and created["n"] == 0


def test_get_or_create_crea_si_no_existe(monkeypatch):
    async def _find(name): return None
    async def _create(name, description=""): return "NUEVO"
    monkeypatch.setattr(zp, "find_profile_by_name", _find)
    monkeypatch.setattr(zp, "create_profile", _create)
    assert asyncio.run(zp.get_or_create_profile("X · uuid")) == "NUEVO"
