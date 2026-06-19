"""B-2 headless · tests del state firmado (_zernio_state) + el callback de retorno (zernio_callback).
Cubre: roundtrip firma, firma forjada → None, 400 firma inválida, AISLAMIENTO (profileId mismatch),
FB select_page gated (needs_page), éxito persiste + connected, y 422-sin-guardar → error. G9 exime tests."""
import asyncio
import pytest
from fastapi import HTTPException

import app.api.routes.oauth._oauth_config as oauth_cfg
from app.api.routes.clients_v3 import _zernio_state as stmod
from app.api.routes.clients_v3.handlers import zernio_callback as cb


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setenv("OAUTH_ENCRYPTION_KEY", "test-hmac-key-123")
    oauth_cfg._oauth_settings = None      # reset lazy singleton → relee la key del env
    yield
    oauth_cfg._oauth_settings = None


def _run(**kw):
    return asyncio.run(cb.zernio_callback(**kw))


def test_callback_bad_state_400():
    with pytest.raises(HTTPException) as e:
        _run(st="forged.x.y.z", profileId="p1", accountId="a1")
    assert e.value.status_code == 400


def test_callback_profile_mismatch_redirects_error(monkeypatch):
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "REAL"})
    resp = _run(st=stmod.sign_state("client-A", "instagram"), profileId="OTHER", accountId="a1")
    assert resp.status_code == 302 and "zernio=error" in resp.headers["location"]


def test_callback_select_page_stashea_sin_tokens_en_url(monkeypatch):
    from app.api.routes.clients_v3.handlers import _zernio_pending as pend
    pend._store.clear()
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "P"})
    resp = _run(st=stmod.sign_state("client-A", "facebook", "", "user-7"), profileId="P", step="select_page",
                tempToken="ttSEC", connect_token="ctSEC")
    loc = resp.headers["location"]
    assert "zernio=needs_page" in loc and "ttSEC" not in loc and "ctSEC" not in loc   # tokens NO en URL
    assert pend.get_pending("user-7", "client-A", "facebook") == ("ttSEC", "ctSEC")   # keyed por user_id (firmado)


def test_callback_success_persists_and_connected(monkeypatch):
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "P"})
    called = {}

    async def _persist(client_id, platform, profile_id, account_id=None):
        called.update(client_id=client_id, platform=platform, profile_id=profile_id, account_id=account_id)
        return {"zernio_account_id": account_id, "handle": "h"}

    monkeypatch.setattr(cb, "persist_zernio_account", _persist)
    resp = _run(st=stmod.sign_state("client-A", "instagram"), profileId="P", accountId="acc1")
    assert called == {"client_id": "client-A", "platform": "instagram",
                      "profile_id": "P", "account_id": "acc1"}
    assert "zernio=connected" in resp.headers["location"]


def test_callback_persist_422_redirects_error(monkeypatch):
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "P"})

    async def _persist(*a, **k):
        raise HTTPException(status_code=422, detail="zernio_account_not_in_profile")

    monkeypatch.setattr(cb, "persist_zernio_account", _persist)
    resp = _run(st=stmod.sign_state("client-A", "instagram"), profileId="P", accountId="acc1")
    assert "zernio=error" in resp.headers["location"]


def _ok_persist():
    async def _p(*a, **k):
        return {"zernio_account_id": "x", "handle": "h"}
    return _p


def test_callback_redirige_al_origen_firmado_si_esta_permitido(monkeypatch):
    monkeypatch.setattr(cb.settings, "backend_cors_origins",
                        "https://www.omegaraisen.agency,https://omegaraisen.agency")
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "P"})
    monkeypatch.setattr(cb, "persist_zernio_account", _ok_persist())
    s = stmod.sign_state("client-A", "instagram", "https://www.omegaraisen.agency")
    resp = _run(st=s, profileId="P", accountId="acc1")
    assert resp.headers["location"].startswith("https://www.omegaraisen.agency/zernio/return")


def test_callback_rechaza_origen_no_permitido_open_redirect(monkeypatch):
    # origen FIRMADO pero NO en la allowlist → NO redirige ahí (anti open-redirect) → cae al [0] permitido.
    monkeypatch.setattr(cb.settings, "backend_cors_origins",
                        "https://www.omegaraisen.agency,https://omegaraisen.agency")
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "P"})
    monkeypatch.setattr(cb, "persist_zernio_account", _ok_persist())
    s = stmod.sign_state("client-A", "instagram", "https://evil.example")
    resp = _run(st=s, profileId="P", accountId="acc1")
    loc = resp.headers["location"]
    assert "evil.example" not in loc                                   # NO redirige al origen forjado/ajeno
    assert loc.startswith("https://www.omegaraisen.agency/zernio/return")   # cae al [0] permitido
