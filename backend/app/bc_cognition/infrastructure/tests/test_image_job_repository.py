"""image_job_repository · CRUD del job pattern de imagen (DEBT-IMAGE-ASYNC F1). G9 exime tests.
Fake supabase captura payloads · verifica el status correcto en cada transición + insert→id."""
import pytest

from app.bc_cognition.infrastructure import image_job_repository as repo


class _Q:
    def __init__(self, store): self._store = store
    def insert(self, payload): self._store["insert"] = payload; return self
    def update(self, payload): self._store["update"] = payload; return self
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def limit(self, *a, **k): return self
    def execute(self): return type("R", (), {"data": self._store["rows"]})()


class _Client:
    def __init__(self, rows): self.store = {"rows": rows}
    def table(self, name): return _Q(self.store)


def _patch(monkeypatch, rows):
    c = _Client(rows)
    monkeypatch.setattr(repo, "get_supabase_service", lambda: type("S", (), {"client": c})())
    return c


def test_insert_pending_devuelve_id_y_status(monkeypatch):
    c = _patch(monkeypatch, [{"id": "job1"}])
    out = repo.insert_pending_job("c1", "un gato", "1024x1024", "standard", {"style": "realistic"})
    assert out == "job1"
    assert c.store["insert"]["status"] == "pending"
    assert c.store["insert"]["client_id"] == "c1" and c.store["insert"]["size"] == "1024x1024"
    assert c.store["insert"]["metadata"] == {"style": "realistic"}


def test_insert_sin_data_levanta(monkeypatch):
    _patch(monkeypatch, [])
    with pytest.raises(RuntimeError):
        repo.insert_pending_job("c1", "x", "1024x1024", "standard")


def test_update_completed_setea_image_url(monkeypatch):
    c = _patch(monkeypatch, [{"id": "job1"}])
    repo.update_job_completed("job1", "https://x/img.png", {"model": "nano"})
    assert c.store["update"]["status"] == "completed"
    assert c.store["update"]["image_url"] == "https://x/img.png" and "completed_at" in c.store["update"]


def test_update_failed_trunca_error_a_500(monkeypatch):
    c = _patch(monkeypatch, [{"id": "job1"}])
    repo.update_job_failed("job1", "E" * 999)
    assert c.store["update"]["status"] == "failed" and len(c.store["update"]["error"]) == 500


def test_update_running_y_cancelled(monkeypatch):
    c = _patch(monkeypatch, [{"id": "job1"}])
    repo.update_job_running("job1")
    assert c.store["update"]["status"] == "running" and "started_at" in c.store["update"]
    repo.update_job_cancelled("job1")
    assert c.store["update"]["status"] == "cancelled"


def test_fetch_job(monkeypatch):
    _patch(monkeypatch, [{"id": "job1", "status": "pending"}])
    assert repo.fetch_job("job1")["status"] == "pending"
