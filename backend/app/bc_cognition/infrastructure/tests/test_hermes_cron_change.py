"""HERMES cron insert-on-change (fix cron↔usage · preserva last_use). G9 exime tests.
Fake supabase cuenta inserts vs updates · garantía clave: el UPDATE del cron NO toca last_use."""
import asyncio
from app.bc_cognition.infrastructure import hermes_checks as hc


class _FakeQuery:
    def __init__(self, store, last_status):
        self._store, self._last = store, last_status
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def insert(self, row): self._store["inserts"].append(row); return self
    def update(self, row): self._store["updates"].append(row); return self
    def execute(self):
        data = [{"id": "x1", "status": self._last}] if self._last is not None else []
        return type("R", (), {"data": data})()


class _FakeClient:
    def __init__(self, last_status):
        self.store = {"inserts": [], "updates": []}
        self._last = last_status
    def table(self, name): return _FakeQuery(self.store, self._last)


def test_apply_check_mismo_estado_update_preserva_last_use():
    """CLAVE del fix: mismo estado → UPDATE solo checked_at · NO toca last_use (cron no es uso)."""
    sb = _FakeClient(last_status="ok")
    res = hc._apply_check(sb, "anthropic", "ok", None)
    assert res == "update"
    assert len(sb.store["updates"]) == 1 and len(sb.store["inserts"]) == 0
    upd = sb.store["updates"][0]
    assert "checked_at" in upd and "last_use" not in upd  # ← garantía: no pisa last_use


def test_apply_check_cambio_estado_inserta():
    """Estado cambió (ok→no_configurado) → INSERT fila nueva con last_use=None."""
    sb = _FakeClient(last_status="ok")
    res = hc._apply_check(sb, "anthropic", "no_configurado", "ANTHROPIC_API_KEY ausente")
    assert res == "insert"
    assert sb.store["inserts"][0]["status"] == "no_configurado"
    assert sb.store["inserts"][0]["last_use"] is None


def test_apply_check_primera_vez_inserta():
    sb = _FakeClient(last_status=None)
    assert hc._apply_check(sb, "brave", "ok", None) == "insert"


def test_run_ping_usa_insert_on_change(monkeypatch):
    """run_hermes_ping aplica _apply_check a cada integración registrada · estado conocido coincide → UPDATE (no INSERT)."""
    for env in set(hc._INTEGRATIONS.values()):
        monkeypatch.setenv(env, "x")  # todas configuradas → 'ok'
    sb = _FakeClient(last_status="ok")
    monkeypatch.setattr(hc, "get_supabase_service", lambda: type("S", (), {"client": sb})())
    out = asyncio.run(hc.run_hermes_ping())
    n = len(hc._INTEGRATIONS)  # conteo dinámico del registro real (cero hardcode)
    assert out["checked"] == n and out["inserted"] == 0  # estado igual → updates, no inserts
    assert len(sb.store["updates"]) == n and len(sb.store["inserts"]) == 0


def test_apply_check_no_tapa_last_use_failed():
    """H7 (endurecimiento): última fila = last_use_failed (caída real del usage). Config presente
    (status ok) NO inserta fila ok encima · refresca checked_at (la miré) sin cambiar status ni
    last_use → el semáforo sigue rojo hasta que un USO real exitoso lo levante."""
    sb = _FakeClient(last_status="last_use_failed")
    res = hc._apply_check(sb, "anthropic", "ok", None)  # config presente → status ok
    assert res == "update"                               # NO insertó 'ok' encima del fallo
    assert len(sb.store["inserts"]) == 0
    upd = sb.store["updates"][0]
    assert "checked_at" in upd                           # sí refrescó "lo chequeé"
    assert "status" not in upd and "last_use" not in upd  # NO mintió salud · NO pisó last_use
