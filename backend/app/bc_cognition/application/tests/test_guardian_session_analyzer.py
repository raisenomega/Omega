"""Tests use case guardian_session_analyzer · 4 casos. Spec §2/§6/§7.4 (fail-open)."""
from datetime import datetime, timedelta, timezone
import app.bc_cognition.application.guardian_session_analyzer as gsa
from app.bc_cognition.domain.guardian_threats import SecurityEvent, SessionAction


def _now():
    return datetime.now(timezone.utc)


class _FakeRepo:
    def __init__(self, recent=(), watchlist=None, fail=False):
        self.recent, self.watchlist, self.fail = recent, watchlist, fail
        self.logs, self.incidents = [], []

    def fetch_recent_events(self, sb, user_id, hours=24):
        if self.fail:
            raise RuntimeError("db down")
        return self.recent

    def lookup_ip(self, sb, ip):
        return self.watchlist

    def insert_security_log(self, sb, *a, **k):
        self.logs.append((a, k))

    def insert_incident(self, sb, *a, **k):
        self.incidents.append((a, k))


def _patch(monkeypatch, fake):
    monkeypatch.setattr(gsa, "repo", fake)
    monkeypatch.setattr(gsa, "get_supabase_service", lambda: object())


def test_happy_clean_allow_logs_no_incident(monkeypatch):
    fake = _FakeRepo(recent=(SecurityEvent("login_success", "1.1.1.1", "ua", _now() - timedelta(hours=1)),))
    _patch(monkeypatch, fake)
    a, err = gsa.analyze_login("u1", "1.1.1.1", "ua", True)
    assert err is None and a.action == SessionAction.ALLOW
    assert len(fake.logs) == 1 and fake.incidents == []


def test_edge_new_device_flag_logged(monkeypatch):
    fake = _FakeRepo(recent=(SecurityEvent("login_success", "1.1.1.1", "ua", _now() - timedelta(hours=1)),))
    _patch(monkeypatch, fake)
    a, err = gsa.analyze_login("u1", "2.2.2.2", "ua", True)
    assert err is None and a.action == SessionAction.FLAG and len(fake.logs) == 1


def test_error_repo_failure_fail_open(monkeypatch):
    _patch(monkeypatch, _FakeRepo(fail=True))
    a, err = gsa.analyze_login("u1", "1.1.1.1", "ua", True)
    assert a is None and err is not None and err.code == "guardian_failure"


def test_boundary_brute_force_block_inserts_incident(monkeypatch):
    recent = tuple(SecurityEvent("login_failed", "9.9.9.9", "ua", _now() - timedelta(minutes=m)) for m in (1, 2, 3, 4, 5))
    fake = _FakeRepo(recent=recent)
    _patch(monkeypatch, fake)
    a, err = gsa.analyze_login("u1", "1.1.1.1", "ua", False)
    assert err is None and a.action == SessionAction.BLOCK and len(fake.incidents) == 1
