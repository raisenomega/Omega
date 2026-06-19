"""B-2 FB · stash in-memory de tokens pendientes (_zernio_pending) · set/get/expiry/clear + key por
(user_id, client_id, platform) (defensa-en-profundidad). G9 exime tests."""
from app.api.routes.clients_v3.handlers import _zernio_pending as pend


def test_stash_y_get():
    pend._store.clear()
    pend.stash_pending("u1", "c1", "facebook", "tt", "ct")
    assert pend.get_pending("u1", "c1", "facebook") == ("tt", "ct")


def test_get_ausente_es_none():
    pend._store.clear()
    assert pend.get_pending("u1", "c1", "facebook") is None


def test_key_ata_user_client_platform():
    pend._store.clear()
    pend.stash_pending("u1", "c1", "facebook", "tt", "ct")
    assert pend.get_pending("u2", "c1", "facebook") is None    # OTRO user → no entrega (defensa-en-profundidad)
    assert pend.get_pending("u1", "c2", "facebook") is None    # otro client
    assert pend.get_pending("u1", "c1", "instagram") is None   # otra platform


def test_expiry_devuelve_none():
    pend._store.clear()
    pend.stash_pending("u1", "c1", "facebook", "tt", "ct")
    k = pend._key("u1", "c1", "facebook")
    t, c, _ = pend._store[k]
    pend._store[k] = (t, c, 0.0)   # expires_at en el pasado → vencido
    assert pend.get_pending("u1", "c1", "facebook") is None


def test_clear():
    pend._store.clear()
    pend.stash_pending("u1", "c1", "facebook", "tt", "ct")
    pend.clear_pending("u1", "c1", "facebook")
    assert pend.get_pending("u1", "c1", "facebook") is None
