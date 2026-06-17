"""Aislamiento del binding Zernio · blinda el incidente del 8-jun (NO solo verifica en abstracto).
get_zernio_account_id(client_id, platform) DEBE devolver la cuenta del negocio correcto y NUNCA
la de otro, aunque ambos tengan cuenta en la MISMA plataforma en el workspace Zernio."""
import importlib
from types import SimpleNamespace

reader = importlib.import_module("app.api.routes.clients_v3._clients_reader")


class _Q:
    """Fake del query builder de Supabase · honra .eq() + .not_.is_(null) + .limit()."""
    def __init__(self, rows): self.rows = rows; self._eqs = {}; self._notnull = None; self._lim = None
    def select(self, *a, **k): return self
    def eq(self, col, val): self._eqs[col] = val; return self
    @property
    def not_(self): return self
    def is_(self, col, val):
        if val == "null": self._notnull = col
        return self
    def limit(self, n): self._lim = n; return self
    def execute(self):
        out = [r for r in self.rows if all(r.get(k) == v for k, v in self._eqs.items())]
        if self._notnull: out = [r for r in out if r.get(self._notnull) is not None]
        return SimpleNamespace(data=(out[: self._lim] if self._lim else out))


def _patch(monkeypatch, rows):
    monkeypatch.setattr(reader, "_sb", lambda: SimpleNamespace(table=lambda t: _Q(rows)))


def test_dos_negocios_misma_plataforma_no_cruzan(monkeypatch):
    # Escenario EXACTO 8-jun: Zafacones IG y Omega Raisen IG conviven en el workspace Zernio.
    rows = [
        {"client_id": "zafa", "platform": "instagram", "zernio_account_id": "ig_zafa"},
        {"client_id": "omega", "platform": "instagram", "zernio_account_id": "ig_raisen"},
    ]
    _patch(monkeypatch, rows)
    assert reader.get_zernio_account_id("zafa", "instagram") == "ig_zafa"
    assert reader.get_zernio_account_id("omega", "instagram") == "ig_raisen"   # NUNCA ig_zafa


def test_filtra_por_client_id_y_platform(monkeypatch):
    rows = [
        {"client_id": "zafa", "platform": "instagram", "zernio_account_id": "ig_zafa"},
        {"client_id": "zafa", "platform": "tiktok", "zernio_account_id": "tt_zafa"},
    ]
    _patch(monkeypatch, rows)
    assert reader.get_zernio_account_id("zafa", "tiktok") == "tt_zafa"
    assert reader.get_zernio_account_id("zafa", "facebook") is None            # sin fila → None


def test_binding_null_devuelve_none(monkeypatch):
    # cuenta sin zernio_account_id (estado actual de las 17) → None → publish falla honesto, no adivina.
    _patch(monkeypatch, [{"client_id": "zafa", "platform": "instagram", "zernio_account_id": None}])
    assert reader.get_zernio_account_id("zafa", "instagram") is None
