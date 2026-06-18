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


def test_sign_verify_roundtrip():
    s = stmod.sign_state("client-A", "instagram")
    assert stmod.verify_state(s) == ("client-A", "instagram")


def test_verify_tampered_sig_is_none():
    s = stmod.sign_state("client-A", "instagram")
    tampered = s[:-1] + ("0" if s[-1] != "0" else "1")
    assert stmod.verify_state(tampered) is None


def test_verify_wrong_shape_is_none():
    assert stmod.verify_state("a.b.c") is None
    assert stmod.verify_state("garbage") is None


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


def test_callback_select_page_is_gated(monkeypatch):
    monkeypatch.setattr(cb.reader, "get_client", lambda cid: {"id": cid, "zernio_profile_id": "P"})
    resp = _run(st=stmod.sign_state("client-A", "facebook"), profileId="P", step="select_page")
    assert "zernio=needs_page" in resp.headers["location"]   # FB no se persiste a ciegas


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
