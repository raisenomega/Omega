"""HERMES Capa 1 · chequeo liviano (DEBT-HERMES-CORE f1). G9 exime tests.
Verifica: credencial presente→ok · ausente→no_configurado · run_hermes_ping best-effort."""
import asyncio
from app.bc_cognition.infrastructure import hermes_checks as hc


def test_build_rows_cubre_las_8_integraciones():
    rows = hc.build_health_rows()
    assert len(rows) == 8
    assert {r["integration"] for r in rows} == set(hc._INTEGRATIONS.keys())
    # todas con status válido del enum + last_use None en fase 1
    for r in rows:
        assert r["status"] in ("ok", "no_configurado")
        assert r["last_use"] is None


def test_credencial_presente_da_ok(monkeypatch):
    monkeypatch.setenv("BRAVE_API_KEY", "algo")
    row = next(r for r in hc.build_health_rows() if r["integration"] == "brave")
    assert row["status"] == "ok"
    assert row["detail"] is None


def test_credencial_ausente_da_no_configurado(monkeypatch):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    row = next(r for r in hc.build_health_rows() if r["integration"] == "brave")
    assert row["status"] == "no_configurado"
    assert "BRAVE_API_KEY" in str(row["detail"])


def test_credencial_solo_espacios_es_no_configurado(monkeypatch):
    monkeypatch.setenv("VOYAGE_API_KEY", "   ")  # whitespace → no cuenta
    row = next(r for r in hc.build_health_rows() if r["integration"] == "voyage")
    assert row["status"] == "no_configurado"


def test_run_ping_best_effort_no_lanza_si_insert_falla(monkeypatch):
    """Si el insert a Supabase falla, el cron NO se rompe (retorna inserted=0)."""
    class _Boom:
        @property
        def client(self):
            raise RuntimeError("supabase down")
    monkeypatch.setattr(hc, "get_supabase_service", lambda: _Boom())
    out = asyncio.run(hc.run_hermes_ping())
    assert out["checked"] == 8 and out["inserted"] == 0  # no lanzó · contó igual
