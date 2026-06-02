"""use_image_job · worker async + DÉBITO SOLO en 'completed' (P1 facturación · plata real). G9 exime tests.
CRÍTICO: job que FALLA → NO debita · job que COMPLETA → debita EXACTAMENTE 1× · cancelado → NO debita.
Todo mockeado (compat/repo/debit/insert) · NO genera ni cobra de verdad."""
import asyncio

from app.bc_cognition.application import use_image_job as uij

_JOB = {"id": "j1", "client_id": "c1", "prompt": "un gato", "size": "1024x1024",
        "quality": "standard", "status": "running", "metadata": {"style": "realistic", "apply_logo": False}}


class _Repo:
    def __init__(self, fetch_responses): self._fetch = list(fetch_responses); self._i = 0; self.calls = []
    def fetch_job(self, jid):
        r = self._fetch[min(self._i, len(self._fetch) - 1)]; self._i += 1
        return dict(r) if r else None
    def update_job_running(self, jid): self.calls.append("running")
    def update_job_completed(self, jid, url, meta): self.calls.append("completed")
    def update_job_failed(self, jid, err): self.calls.append("failed")


async def _compat_ok(**kw): return ["https://x/img.png"]
async def _compat_boom(**kw): raise RuntimeError("gemini 503")


def _wire(monkeypatch, repo, compat):
    monkeypatch.setattr(uij, "repo", repo)
    monkeypatch.setattr(uij, "generate_image_compat", compat)
    monkeypatch.setattr(uij, "cost_for_image", lambda r="default": 0.05)
    debits: list = []
    async def _debit(cid, agent, cost, model=None, execution_id=None): debits.append((cid, cost))
    monkeypatch.setattr(uij, "debit", _debit)
    async def _safe_insert(label, fn, *a, **k): return "content1"
    monkeypatch.setattr(uij.cl_repo, "safe_insert", _safe_insert)
    return debits


def test_completa_debita_exactamente_una_vez(monkeypatch):
    repo = _Repo([_JOB, _JOB])  # fetch inicial + re-check (no cancelado)
    debits = _wire(monkeypatch, repo, _compat_ok)
    asyncio.run(uij._run_image_job("j1", None))
    assert "completed" in repo.calls and "failed" not in repo.calls
    assert len(debits) == 1 and debits[0] == ("c1", 0.05)  # 1 cobro exacto, ni 0 ni doble


def test_falla_NO_debita(monkeypatch):
    repo = _Repo([_JOB, _JOB])
    debits = _wire(monkeypatch, repo, _compat_boom)  # Gemini revienta antes del débito
    asyncio.run(uij._run_image_job("j1", None))
    assert "failed" in repo.calls and "completed" not in repo.calls  # anti-orphan: cae en failed
    assert len(debits) == 0  # NUNCA cobrar una generación que falló


def test_cancelado_midflight_NO_debita(monkeypatch):
    cancelled = dict(_JOB); cancelled["status"] = "cancelled"
    repo = _Repo([_JOB, cancelled])  # 2da fetch = cancelado mid-flight
    debits = _wire(monkeypatch, repo, _compat_ok)
    asyncio.run(uij._run_image_job("j1", None))
    assert len(debits) == 0 and "completed" not in repo.calls  # no persiste ni cobra
