"""P1-7 (Fase 2) · CORS fail-secure.

Orígenes vacíos en producción → RuntimeError en boot (jamás wildcard en prod ·
un typo en la env var abriría CORS al mundo). Dev → ['*']. Con orígenes → tal cual."""
import pytest

from app.config import resolve_cors_origins


def test_prod_vacia_raise():
    with pytest.raises(RuntimeError):
        resolve_cors_origins([], "production")


def test_dev_vacia_wildcard():
    assert resolve_cors_origins([], "development") == ["*"]


def test_con_origenes_tal_cual():
    assert resolve_cors_origins(["https://app.com"], "production") == ["https://app.com"]
    assert resolve_cors_origins(["https://a.com", "https://b.com"], "development") == ["https://a.com", "https://b.com"]
