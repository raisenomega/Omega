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


def test_sign_verify_roundtrip():
    s = stmod.sign_state("client-A", "instagram", "https://www.omegaraisen.agency")
    assert stmod.verify_state(s) == ("client-A", "instagram", "https://www.omegaraisen.agency")


def test_verify_tampered_sig_is_none():
    s = stmod.sign_state("client-A", "instagram", "https://x.test")
    tampered = s[:-1] + ("0" if s[-1] != "0" else "1")
    assert stmod.verify_state(tampered) is None


def test_verify_wrong_shape_is_none():
    assert stmod.verify_state("a.b.c") is None     # 3 segmentos, no 5
    assert stmod.verify_state("garbage") is None
