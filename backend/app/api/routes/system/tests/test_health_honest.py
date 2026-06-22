"""/health honesto · status derivado del conteo real · sin fallback 37 ni tautología N/N.
Mata FG1 (status hardcodeado) · FG2 (count else 37 + except 37) · FG3 ('37/37')."""
import app.api.routes.system.handlers.get_stats as gs


# --- fakes mínimos del cliente Supabase (chain table->select->eq->execute->.count) ---
class _Resp:
    def __init__(self, count): self.count = count

class _Q:
    def __init__(self, count): self._c = count
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def execute(self): return _Resp(self._c)

class _SB:
    def __init__(self, count):
        self.client = type("C", (), {"table": lambda _s, *a, **k: _Q(count)})()


def test_count_active_agents_real(monkeypatch):
    monkeypatch.setattr(gs, "get_supabase_service", lambda: _SB(37))
    assert gs.count_active_agents() == 37


def test_count_active_agents_cero_real_no_es_none(monkeypatch):
    """0 REAL se respeta como 0 (no se confunde con fallo · FG2)."""
    monkeypatch.setattr(gs, "get_supabase_service", lambda: _SB(0))
    assert gs.count_active_agents() == 0


def test_count_active_agents_falla_devuelve_none(monkeypatch):
    """DB caída → None (NO inventa 37 · esa era la mentira de FG2)."""
    def _boom(): raise RuntimeError("db down")
    monkeypatch.setattr(gs, "get_supabase_service", _boom)
    assert gs.count_active_agents() is None


def test_build_health_healthy():
    out = gs.build_health(37, "abc1234", "production")
    assert out["status"] == "healthy" and out["agents_active"] == 37
    assert out["git_sha"] == "abc1234" and "detail" not in out


def test_build_health_degraded_unavailable():
    """None (falló el conteo) → degraded honesto, sin inventar número (FG1+FG2)."""
    out = gs.build_health(None, "abc1234", "production")
    assert out["status"] == "degraded" and out["detail"] == "agents_count_unavailable"
    assert "agents_active" not in out


def test_build_health_degraded_zero():
    """0 agentes → degraded (problema real · ya no enmascarado por el else 37)."""
    out = gs.build_health(0, "abc1234", "production")
    assert out["status"] == "degraded" and out["detail"] == "no_active_agents"


def test_build_health_blindaje_anti_regresion():
    """Anti-reintroducción de los false-greens exactos: nunca '37/37' ni fallback 37."""
    healthy = gs.build_health(5, "s", "production")
    assert "/" not in str(healthy["agents_active"])     # FG3: jamás la tautología "N/N"
    failed = gs.build_health(None, "s", "production")
    assert 37 not in failed.values()                    # FG2: jamás inventa 37
    assert failed["status"] != "healthy"                # FG1: status NO es siempre healthy
