"""Punto 6 · Commit A · bloque INVENTARIO DE CAPACIDADES (autoconciencia de NOVA).
Numéricos en vivo + manifiesto curado · fail-safe POR query · cache · cero accuracy %."""
import os
from types import SimpleNamespace
from unittest.mock import patch

from app.api.routes.nova.handlers import _capabilities as cap


class _Q:
    def __init__(self, data, raise_exc=False):
        self._d, self._raise = data, raise_exc
    def select(self, *a, **k): return self
    def order(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def eq(self, *a, **k): return self
    @property
    def not_(self): return self
    def is_(self, *a, **k): return self
    def execute(self):
        if self._raise:
            raise RuntimeError("db down")
        return SimpleNamespace(data=self._d)


def _svc(sentinel=None, aria=None, sraise=False, araise=False):
    def table(name):
        return _Q(sentinel or [], sraise) if name == "sentinel_scans" else _Q(aria or [], araise)
    return SimpleNamespace(client=SimpleNamespace(table=table))


def _build(svc=None, sha="abc1234def"):
    cap._cache = None; cap._cache_time = None
    with patch.dict(os.environ, {"RAILWAY_GIT_COMMIT_SHA": sha}), \
         patch.object(cap, "get_supabase_service", return_value=svc if svc is not None else _svc()):
        return cap.build_capabilities_block()


def test_block_has_real_capabilities():
    b = _build(_svc(sentinel=[{"security_score": 86}], aria=[]))
    assert "=== INVENTARIO DE CAPACIDADES" in b and "git abc1234" in b   # sha[:7]
    assert "4 chains" in b and "content_generation" in b and "full_analysis" in b
    assert "8 operativos" in b and "nova_chat" in b and "sentinel_security" in b
    assert "security_score 86/100" in b
    assert "Loop de verdad: 0 interacciones con veredicto real cerrado" in b


def test_no_hecho_lines_present():
    b = _build(_svc(sentinel=[{"security_score": 80}]))
    assert "GAP-2" in b and "(2.1)" in b and "F1.5" in b
    assert "VIVO Y VERIFICADO:" in b and "AÚN NO HECHO" in b


def test_no_percentage_or_accuracy():
    b = _build(_svc(sentinel=[{"security_score": 90}]))
    assert "%" not in b and "accuracy" not in b.lower()


def test_regla_p1_prohibe_completitud_agregada():
    # La regla ataca el AGREGADO (no solo el %): porcentaje/fracción/etiqueta global.
    b = _build(_svc(sentinel=[{"security_score": 90}]))
    assert "No inventes un grado de completitud global" in b
    assert "sin agregarlas en un puntaje" in b


def test_real_verdict_count_excludes_api_failures():
    # 1 True real + 1 False [failed:] (no cuenta) + 1 False real → with_real_verdict=2
    aria = [{"was_correct": True, "decision": "ok"},
            {"was_correct": False, "decision": "[failed:api_error]"},
            {"was_correct": False, "decision": "rechazado real"}]
    b = _build(_svc(sentinel=[{"security_score": 70}], aria=aria))
    assert "Loop de verdad: 2 interacciones" in b


def test_failsafe_per_query_independent():
    # score falla → n/d en SU línea · verdict-count OK → presente. Bloque siempre sale.
    b = _build(_svc(sraise=True, aria=[]))
    assert "security_score n/d/100" in b and "Loop de verdad: 0 interacciones" in b
    # verdict falla → n/d · score OK
    b2 = _build(_svc(sentinel=[{"security_score": 88}], araise=True))
    assert "security_score 88/100" in b2 and "Loop de verdad: n/d interacciones" in b2


def test_failsafe_no_supabase_block_still_renders():
    cap._cache = None; cap._cache_time = None
    with patch.dict(os.environ, {"RAILWAY_GIT_COMMIT_SHA": "deadbeef"}), \
         patch.object(cap, "get_supabase_service", side_effect=RuntimeError("no db")):
        b = cap.build_capabilities_block()
    assert "=== INVENTARIO DE CAPACIDADES" in b
    assert "security_score n/d/100" in b and "Loop de verdad: n/d" in b


def test_cache_returns_same_within_ttl():
    svc = _svc(sentinel=[{"security_score": 50}], aria=[])
    first = _build(svc)
    # segunda llamada SIN resetear cache → debe devolver el cacheado aunque cambie la data
    with patch.object(cap, "get_supabase_service", return_value=_svc(sentinel=[{"security_score": 999}])):
        second = cap.build_capabilities_block()
    assert first == second and "50/100" in second and "999" not in second
