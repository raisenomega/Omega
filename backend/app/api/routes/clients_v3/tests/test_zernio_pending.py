"""B-2 FB · stash in-memory de tokens pendientes (_zernio_pending) · set/get/expiry/clear. G9 exime tests."""
from app.api.routes.clients_v3.handlers import _zernio_pending as pend


def test_stash_y_get():
    pend._store.clear()
    pend.stash_pending("c1", "facebook", "tt", "ct")
    assert pend.get_pending("c1", "facebook") == ("tt", "ct")


def test_get_ausente_es_none():
    pend._store.clear()
    assert pend.get_pending("c1", "facebook") is None


def test_key_por_client_y_platform():
    pend._store.clear()
    pend.stash_pending("c1", "facebook", "tt", "ct")
    assert pend.get_pending("c1", "instagram") is None   # otra platform = otra key
    assert pend.get_pending("c2", "facebook") is None     # otro client = otra key


def test_expiry_devuelve_none(monkeypatch):
    pend._store.clear()
    pend.stash_pending("c1", "facebook", "tt", "ct")
    k = pend._key("c1", "facebook")
    t, c, _ = pend._store[k]
    pend._store[k] = (t, c, 0.0)   # expires_at en el pasado → vencido
    assert pend.get_pending("c1", "facebook") is None


def test_clear():
    pend._store.clear()
    pend.stash_pending("c1", "facebook", "tt", "ct")
    pend.clear_pending("c1", "facebook")
    assert pend.get_pending("c1", "facebook") is None
