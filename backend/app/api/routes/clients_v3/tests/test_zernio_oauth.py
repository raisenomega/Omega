"""B-2 · ensure-profile / connect-url / connected-accounts · ownership + reuso de profile (G9 exime tests)."""
import asyncio
import importlib

import pytest
from fastapi import HTTPException

from app.bc_cognition.infrastructure.zernio_adapter import ZernioPublishError

zo = importlib.import_module("app.api.routes.clients_v3.handlers.zernio_oauth")


def _auth(monkeypatch, client, owns=True):
    async def _user(a): return {"id": "u1"}
    monkeypatch.setattr(zo, "get_current_user", _user)
    monkeypatch.setattr(zo.reader, "get_client", lambda cid: client)
    monkeypatch.setattr(zo, "user_owns_client", lambda uid, c: owns)


def test_ensure_profile_403_si_no_dueno(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u2"}, owns=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zo.ensure_zernio_profile("c1", "auth"))
    assert e.value.status_code == 403


def test_ensure_profile_crea_si_falta_y_guarda(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "name": "Zafacones", "zernio_profile_id": None})
    saved = {}
    async def _create(name, description=""): return "prof_new"
    monkeypatch.setattr(zo, "create_profile", _create)
    monkeypatch.setattr(zo.repo, "update_client_by_id", lambda cid, f: saved.update(f) or 1)
    out = asyncio.run(zo.ensure_zernio_profile("c1", "auth"))
    assert out["zernio_profile_id"] == "prof_new" and saved["zernio_profile_id"] == "prof_new"


def test_ensure_profile_reusa_si_existe(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    called = {"create": False}
    async def _create(name, description=""): called["create"] = True; return "X"
    monkeypatch.setattr(zo, "create_profile", _create)
    out = asyncio.run(zo.ensure_zernio_profile("c1", "auth"))
    assert out["zernio_profile_id"] == "prof_ya" and called["create"] is False   # NO recrea


def test_connect_url_devuelve_auth_url(monkeypatch):
    # connect-url ahora va HEADLESS: firma el state (necesita OAUTH_ENCRYPTION_KEY) y pasa redirect_url.
    import app.api.routes.oauth._oauth_config as oauth_cfg
    monkeypatch.setenv("OAUTH_ENCRYPTION_KEY", "test-hmac-key-123")
    oauth_cfg._oauth_settings = None
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    captured = {}
    async def _cu(platform, pid, redirect_url=None):
        captured["redirect_url"] = redirect_url
        return f"https://www.facebook.com/oauth?profileId={pid}"
    monkeypatch.setattr(zo, "get_connect_url", _cu)
    out = asyncio.run(zo.zernio_connect_url("c1", "facebook", "auth"))
    assert "facebook.com" in out["auth_url"] and "prof_ya" in out["auth_url"]
    # el redirect_url debe apuntar al callback de OMEGA con un state firmado (headless · vuelve a casa)
    assert "/clients/zernio/callback?st=" in captured["redirect_url"]


def test_connected_accounts_lista_del_profile(monkeypatch):
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    async def _la(pid): return [{"_id": "ig1", "platform": "instagram", "username": "@z"}]
    monkeypatch.setattr(zo, "list_accounts", _la)
    out = asyncio.run(zo.zernio_connected_accounts("c1", "auth"))
    assert out["profile"] == "prof_ya" and out["items"][0]["zernio_account_id"] == "ig1"


def test_connected_accounts_followers_real_del_profile(monkeypatch):
    """(a) followersCount REAL viaja en el item para cuentas de ESTE profile."""
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    async def _la(pid):
        return [{"_id": "ig1", "platform": "instagram", "username": "@z",
                 "profileId": "prof_ya", "followersCount": 1234}]
    monkeypatch.setattr(zo, "list_accounts", _la)
    out = asyncio.run(zo.zernio_connected_accounts("c1", "auth"))
    assert out["items"][0]["followers_count"] == 1234   # real de Zernio, no inventado


def test_connected_accounts_followers_aislados_por_profile(monkeypatch):
    """(b) AISLAMIENTO: el followersCount de OTRO negocio NO se cuela (profile no casa → None)."""
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    async def _la(pid):
        return [
            {"_id": "ig1", "platform": "instagram", "profileId": "prof_ya", "followersCount": 1234},
            {"_id": "ig2", "platform": "instagram", "profileId": "prof_OTRO", "followersCount": 9999},
        ]
    monkeypatch.setattr(zo, "list_accounts", _la)
    out = asyncio.run(zo.zernio_connected_accounts("c1", "auth"))
    by_id = {i["zernio_account_id"]: i["followers_count"] for i in out["items"]}
    assert by_id["ig1"] == 1234        # el mío sí
    assert by_id["ig2"] is None        # el ajeno NO filtra su número (9999 jamás)


def test_connected_accounts_sin_followers_no_inventa_cero(monkeypatch):
    """(c) sin followersCount → None (la fila muestra '—', NUNCA 0 sintético · P1)."""
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "zernio_profile_id": "prof_ya"})
    async def _la(pid):
        return [{"_id": "ig1", "platform": "instagram", "profileId": "prof_ya"}]  # sin followersCount
    monkeypatch.setattr(zo, "list_accounts", _la)
    out = asyncio.run(zo.zernio_connected_accounts("c1", "auth"))
    assert out["items"][0]["followers_count"] is None   # '—', no 0


# ── B2.5 Capa A · robustez: ZernioError del connect → HTTP honesto, NO 500 crudo ──
def test_connect_url_409_si_nombre_duplicado(monkeypatch):
    """Profile name duplicado (Zernio 400 'already exists') → 409 zernio_profile_name_conflict."""
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "name": "Zafacones", "zernio_profile_id": None})
    async def _boom(name, description=""):
        raise ZernioPublishError('zernio_profiles_400:{"error":"A profile with this name already exists"}')
    monkeypatch.setattr(zo, "create_profile", _boom)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zo.zernio_connect_url("c1", "instagram", "auth", None))
    assert e.value.status_code == 409 and e.value.detail == "zernio_profile_name_conflict"


def test_connect_url_502_si_transporte(monkeypatch):
    """Fallo de transporte a Zernio → 502 zernio_unavailable (no 500 crudo)."""
    _auth(monkeypatch, {"id": "c1", "user_id": "u1", "name": "X", "zernio_profile_id": None})
    async def _boom(name, description=""):
        raise ZernioPublishError("zernio_transport_error:ConnectTimeout")
    monkeypatch.setattr(zo, "create_profile", _boom)
    with pytest.raises(HTTPException) as e:
        asyncio.run(zo.zernio_connect_url("c1", "instagram", "auth", None))
    assert e.value.status_code == 502
