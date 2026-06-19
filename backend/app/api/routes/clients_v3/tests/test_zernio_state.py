"""B-2 headless · tests del state firmado (_zernio_state) · roundtrip con origen, firma forjada → None,
forma inválida → None. Separado de test_zernio_callback para C4 (≤100L). G9 exime tests."""
import pytest

import app.api.routes.oauth._oauth_config as oauth_cfg
from app.api.routes.clients_v3 import _zernio_state as stmod


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setenv("OAUTH_ENCRYPTION_KEY", "test-hmac-key-123")
    oauth_cfg._oauth_settings = None      # reset lazy singleton → relee la key del env
    yield
    oauth_cfg._oauth_settings = None


def test_sign_verify_roundtrip_con_user_id():
    s = stmod.sign_state("client-A", "instagram", "https://www.omegaraisen.agency", "user-9")
    assert stmod.verify_state(s) == ("client-A", "instagram", "https://www.omegaraisen.agency", "user-9")


def test_verify_tampered_sig_is_none():
    s = stmod.sign_state("client-A", "instagram", "https://x.test", "user-9")  # user_id es parte del HMAC
    tampered = s[:-1] + ("0" if s[-1] != "0" else "1")
    assert stmod.verify_state(tampered) is None


def test_verify_wrong_shape_is_none():
    assert stmod.verify_state("a.b.c") is None     # 3 segmentos (ni 5 ni 6)
    assert stmod.verify_state("garbage") is None


def test_verify_5seg_legacy_backcompat():
    """State LEGACY de 5 seg (deploy anterior · sin user_id) sigue verificando → user_id='' (back-comp
    de states en vuelo durante el deploy · estado efímero)."""
    import hashlib
    import hmac
    o = stmod._enc("https://x.test")
    sig = hmac.new(stmod._signing_key(), stmod._msg("cid", "instagram", o, "nz"), hashlib.sha256).hexdigest()
    legacy = f"cid.instagram.{o}.nz.{sig}"
    assert stmod.verify_state(legacy) == ("cid", "instagram", "https://x.test", "")


def _set_base(monkeypatch, value):
    """Setea OAUTH_REDIRECT_BASE y resetea el singleton para que build_callback_url lo relea."""
    monkeypatch.setenv("OAUTH_REDIRECT_BASE", value)
    oauth_cfg._oauth_settings = None


def test_build_callback_url_descarta_path_pegado(monkeypatch):
    # base con path pegado (el bug real de prod) → solo scheme://host en el resultado.
    _set_base(monkeypatch, "https://omega-production-3c67.up.railway.app/api/v1/auth/google/callback")
    assert stmod.build_callback_url("ST") == \
        "https://omega-production-3c67.up.railway.app/api/v1/clients/zernio/callback?st=ST"


def test_build_callback_url_base_vacia_LANZA(monkeypatch):
    # ESTE es el test que hubiera atrapado el 500 de prod (OAUTH_REDIRECT_BASE ausente → vacía).
    _set_base(monkeypatch, "")
    with pytest.raises(RuntimeError):
        stmod.build_callback_url("ST")


def test_build_callback_url_base_sin_host_LANZA(monkeypatch):
    _set_base(monkeypatch, "/api/v1/clients")      # relativa · sin scheme/host → no se manda relativo a Zernio
    with pytest.raises(RuntimeError):
        stmod.build_callback_url("ST")
