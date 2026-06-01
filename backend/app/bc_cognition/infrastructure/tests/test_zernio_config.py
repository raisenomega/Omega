"""Zernio settings · base con default + key desde el entorno. G9 exime tests.
Robusto a que .env tenga o no la key (setenv tiene prioridad sobre .env file en pydantic-settings)."""
from app.bc_cognition.infrastructure.zernio_config import ZernioSettings, get_zernio_settings


def test_base_url_default():
    # ZERNIO_API_BASE no se setea en .env → default canonico (verificado contra docs.zernio.com)
    assert ZernioSettings().zernio_api_base == "https://zernio.com/api/v1"


def test_lee_key_del_entorno(monkeypatch):
    monkeypatch.setenv("ZERNIO_API_KEY", "sk_test_dummy_value")
    assert ZernioSettings().zernio_api_key == "sk_test_dummy_value"


def test_singleton():
    assert get_zernio_settings() is get_zernio_settings()
