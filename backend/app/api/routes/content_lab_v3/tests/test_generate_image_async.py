"""generate_image · flag IMAGE_ASYNC_ENABLED (DEBT-IMAGE-ASYNC F3). G9 exime tests.
OFF → comportamiento síncrono viejo (devuelve imagen + débito síncrono) · ON → job_id (worker · débito
síncrono NO corre) · GET de job ajeno/inexistente → 404 no-leak (P2). Todo mockeado · NO genera ni cobra."""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateImageRequest, GenerateImageResponse, ImageJobStartResponse,
)

gi = importlib.import_module("app.api.routes.content_lab_v3.handlers.generate_image")


async def _user(auth): return {"id": "u1"}
async def _budget_ok(cid): return True


def _common(monkeypatch, async_enabled):
    monkeypatch.setattr(gi, "get_current_user", _user)
    monkeypatch.setattr(gi, "resolve_client_or_403", lambda uid, cid: {"id": "c1"})
    monkeypatch.setattr(gi, "check_budget", _budget_ok)
    monkeypatch.setattr(gi, "get_feature_flags", lambda: SimpleNamespace(image_async_enabled=async_enabled))


def test_flag_off_devuelve_imagen_sincrono(monkeypatch):
    _common(monkeypatch, async_enabled=False)
    n = {"compat": 0, "debit": 0, "job": 0}
    async def _compat(**kw): n["compat"] += 1; return ["https://x/img.png"]
    async def _safe_insert(label, fn, *a, **k): return "content1"
    async def _debit(*a, **k): n["debit"] += 1
    async def _job(*a, **k): n["job"] += 1; return "jobX"
    monkeypatch.setattr(gi, "generate_image_compat", _compat)
    monkeypatch.setattr(gi.repo, "safe_insert", _safe_insert)
    monkeypatch.setattr(gi, "debit", _debit)
    monkeypatch.setattr(gi, "create_image_job", _job)
    out = asyncio.run(gi.generate_image(GenerateImageRequest(prompt="un gato", client_id="c1"), None))
    assert isinstance(out, GenerateImageResponse) and out.generated_text == "https://x/img.png"
    assert n["compat"] == 1 and n["debit"] == 1 and n["job"] == 0  # path viejo intacto · worker NO se llama


def test_flag_on_devuelve_job_id_sin_debito_sincrono(monkeypatch):
    _common(monkeypatch, async_enabled=True)
    n = {"compat": 0, "debit": 0}
    async def _compat(**kw): n["compat"] += 1; return ["x"]
    async def _debit(*a, **k): n["debit"] += 1
    async def _job(*a, **k): return "job123"
    monkeypatch.setattr(gi, "generate_image_compat", _compat)
    monkeypatch.setattr(gi, "debit", _debit)
    monkeypatch.setattr(gi, "create_image_job", _job)
    out = asyncio.run(gi.generate_image(GenerateImageRequest(prompt="un gato", client_id="c1"), None))
    assert isinstance(out, ImageJobStartResponse) and out.job_id == "job123" and out.status == "pending"
    assert n["compat"] == 0 and n["debit"] == 0  # ON: ni compat NI débito síncrono (los hace el worker)


def test_get_status_job_ajeno_404(monkeypatch):
    monkeypatch.setattr(gi, "get_current_user", _user)
    monkeypatch.setattr(gi, "get_image_job", lambda jid: {"client_id": "c2", "status": "completed"})
    monkeypatch.setattr(gi.clients_reader, "get_client", lambda cid: {"id": "c2"})
    monkeypatch.setattr(gi, "user_owns_client", lambda uid, c: False)  # u1 NO es dueño de c2
    with pytest.raises(HTTPException) as ei:
        asyncio.run(gi.get_image_job_status("jobX", None))
    assert ei.value.status_code == 404  # no-leak · no revela que el job ajeno existe


def test_get_status_job_inexistente_404(monkeypatch):
    monkeypatch.setattr(gi, "get_current_user", _user)
    monkeypatch.setattr(gi, "get_image_job", lambda jid: None)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(gi.get_image_job_status("nope", None))
    assert ei.value.status_code == 404


def test_get_status_completed_expone_content_id(monkeypatch):
    # BUG 11 jun: el worker async guarda content_id en metadata (use_image_job:85),
    # pero el status NO lo exponía → el frontend usaba job_id como id → Guardar la
    # imagen daba content_not_found (404). El status debe devolver el content_id real.
    monkeypatch.setattr(gi, "get_current_user", _user)
    monkeypatch.setattr(gi, "get_image_job", lambda jid: {
        "client_id": "c1", "status": "completed", "image_url": "https://x/img.png",
        "metadata": {"content_id": "real-content-uuid", "style": "realistic"},
    })
    monkeypatch.setattr(gi.clients_reader, "get_client", lambda cid: {"id": "c1"})
    monkeypatch.setattr(gi, "user_owns_client", lambda uid, c: True)
    out = asyncio.run(gi.get_image_job_status("jobX", None))
    assert out.content_id == "real-content-uuid"   # ← el frontend usa ESTE id para Guardar
    assert out.image_url == "https://x/img.png"
