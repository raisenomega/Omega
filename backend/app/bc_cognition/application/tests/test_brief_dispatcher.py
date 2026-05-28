"""Tests brief_dispatcher (DEBT-105) · briefs periódicos al owner por email.

AISLADO de alert_dispatcher (path de alarma en prod · no se toca). Best-effort:
ningún fallo de Resend rompe el cron. asyncio.run (sin pytest-asyncio · convención repo).
"""
import asyncio
import app.bc_cognition.application.brief_dispatcher as bd


def _sentinel_result() -> dict:
    return {
        "security_score": 72, "status": "warning", "deploy_decision": "BLOCK",
        "total_issues": 2, "critical_issues": 1, "agents_scanned": 3,
        "issues": [{"severity": "CRITICAL", "message": "RLS off en tabla x"},
                   {"severity": "LOW", "agent_code": "VAULT"}],
    }


def _oracle_brief() -> dict:
    return {
        "week_of": "2026-05-27",
        "executive_summary": {"total_clients": 4, "active_clients": 3,
                              "total_resellers": 1, "sentinel_score": 82},
        "opportunities": [{"priority": "HIGH", "description": "3 clientes Basic upsell a Pro"}],
        "alerts": [{"severity": "MEDIUM", "description": "1 cliente inactivo"}],
        "recommendation": "Escalar adquisicion.",
    }


def test_no_key_skips_email(monkeypatch):
    """Sin RESEND_API_KEY -> _post_resend retorna False · no rompe."""
    monkeypatch.setattr(bd.settings, "resend_api_key", "")
    assert asyncio.run(bd._post_resend("subj", "body")) is False


def test_sentinel_brief_formats_and_sends(monkeypatch):
    """dispatch_sentinel_brief arma subject+body con score/issues y delega en _post_resend."""
    cap = {}

    async def _capture(subject, text):
        cap["subject"], cap["text"] = subject, text
        return True

    monkeypatch.setattr(bd, "_post_resend", _capture)
    assert asyncio.run(bd.dispatch_sentinel_brief(_sentinel_result())) is True
    assert "72/100" in cap["subject"] and "warning" in cap["subject"]
    assert "CRITICAL" in cap["text"] and "RLS off" in cap["text"]


def test_oracle_brief_formats_and_sends(monkeypatch):
    """dispatch_oracle_brief arma el resumen semanal y delega en _post_resend."""
    cap = {}

    async def _capture(subject, text):
        cap["subject"], cap["text"] = subject, text
        return True

    monkeypatch.setattr(bd, "_post_resend", _capture)
    assert asyncio.run(bd.dispatch_oracle_brief(_oracle_brief())) is True
    assert "2026-05-27" in cap["subject"]
    assert "3 clientes Basic" in cap["text"] and "upsell" in cap["text"]


def test_post_resend_best_effort_on_error(monkeypatch):
    """Excepción de httpx -> False (best-effort · no propaga · no rompe el cron)."""
    monkeypatch.setattr(bd.settings, "resend_api_key", "re-test")

    class _Boom:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, *a, **k):
            raise RuntimeError("resend down")

    monkeypatch.setattr(bd.httpx, "AsyncClient", _Boom)
    assert asyncio.run(bd._post_resend("s", "b")) is False
