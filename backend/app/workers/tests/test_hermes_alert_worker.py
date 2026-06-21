"""HERMES alerta inmediata · select_alerts (anti-spam) + best-effort del cron. G9 exime tests."""
import asyncio
from datetime import datetime, timezone, timedelta
import app.workers.hermes_alert_worker as w

_NOW = datetime(2026, 6, 21, 12, 0, 0, tzinfo=timezone.utc)


def _row(integration, status, age_min, detail="zernio_503"):
    return {"integration": integration, "status": status, "detail": detail,
            "created_at": (_NOW - timedelta(minutes=age_min)).isoformat()}


def test_critica_recien_abierta_alerta():
    # (a) zernio recién caído (2 min ≤ ventana) → alerta.
    assert [r["integration"] for r in w.select_alerts([_row("zernio", "last_use_failed", 2)], _NOW)] == ["zernio"]


def test_critica_vieja_no_realerta():
    # (b) ANTI-SPAM: incidente abierto pero VIEJO (30 min > ventana) → NO re-alerta.
    assert w.select_alerts([_row("zernio", "last_use_failed", 30)], _NOW) == []


def test_menor_caida_no_alerta_inmediata():
    # (c) brave NO es crítica → no alerta inmediata (solo resumen diario).
    assert w.select_alerts([_row("brave", "last_use_failed", 1)], _NOW) == []


def test_critica_recuperada_no_alerta():
    # (d) anthropic en 'ok' (recuperada) → no alerta de fallo.
    assert w.select_alerts([_row("anthropic", "ok", 1)], _NOW) == []


def test_cron_best_effort_si_dispatch_lanza_no_rompe(monkeypatch):
    # CRÍTICO: si dispatch_hermes_alert lanza (resend/telegram caído), el cron NO se rompe.
    monkeypatch.setattr(w.hermes_alerts, "latest_critical", lambda: [_row("zernio", "last_use_failed", 1)])
    async def _boom(integration, detail): raise RuntimeError("resend down")
    monkeypatch.setattr(w, "dispatch_hermes_alert", _boom)
    out = asyncio.run(w.run_hermes_alert_check())
    assert out == {"checked": 1, "alerted": 0}  # no explotó · alerted=0 (la notif falló, el cron sigue vivo)


def test_cron_dispatch_ok_cuenta_la_alerta(monkeypatch):
    monkeypatch.setattr(w.hermes_alerts, "latest_critical", lambda: [_row("stripe", "last_use_failed", 1)])
    async def _ok(integration, detail): return True
    monkeypatch.setattr(w, "dispatch_hermes_alert", _ok)
    out = asyncio.run(w.run_hermes_alert_check())
    assert out == {"checked": 1, "alerted": 1}
