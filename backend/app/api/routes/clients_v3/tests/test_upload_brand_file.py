"""POST /clients/{id}/brand-files · ownership check (SEC-002 · IDOR fix Fase C).
Mock de reader/storage · cero DB/Storage real. G9 exime tests."""
import asyncio
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock

from fastapi import HTTPException

from app.api.routes.clients_v3.handlers import upload_brand_file as h

_OWNER = {"id": "u1"}
_CLIENT = {"id": "c1", "user_id": "u1"}


def _file():
    return SimpleNamespace(read=AsyncMock(return_value=b"x"), filename="logo.png", content_type="image/png")


def test_403_cross_owner():
    """Usuario autenticado intenta subir al client_id de OTRO dueño → 403 (no escribe)."""
    with patch.object(h, "get_current_user", AsyncMock(return_value=_OWNER)), \
         patch.object(h.reader, "get_client", return_value={"id": "c1", "user_id": "OTRO"}), \
         patch.object(h, "user_owns_client", return_value=False):
        try:
            asyncio.run(h.upload_brand_file("c1", _file(), "logo", "Bearer x"))
            assert False, "esperaba 403"
        except HTTPException as e:
            assert e.status_code == 403


def test_404_client_inexistente():
    with patch.object(h, "get_current_user", AsyncMock(return_value=_OWNER)), \
         patch.object(h.reader, "get_client", return_value=None):
        try:
            asyncio.run(h.upload_brand_file("c1", _file(), "logo", "Bearer x"))
            assert False, "esperaba 404"
        except HTTPException as e:
            assert e.status_code == 404


def test_happy_path_ownership_valido():
    """Ownership válido → sube a Storage e inserta en brand_files con el client_id correcto."""
    cap = {}
    ins = SimpleNamespace(execute=lambda: SimpleNamespace(data=[{"id": "file-1"}]))
    sb = SimpleNamespace(
        storage=SimpleNamespace(from_=lambda b: SimpleNamespace(
            upload=lambda *a, **k: cap.update(up=a), get_public_url=lambda p: f"https://x/{p}")),
        table=lambda n: SimpleNamespace(insert=lambda p: (cap.update(ins=p) or ins)))
    with patch.object(h, "get_current_user", AsyncMock(return_value=_OWNER)), \
         patch.object(h.reader, "get_client", return_value=_CLIENT), \
         patch.object(h, "user_owns_client", return_value=True), \
         patch.object(h, "_sb", lambda: sb):
        out = asyncio.run(h.upload_brand_file("c1", _file(), "logo", "Bearer x"))
    assert out["id"] == "file-1"
    assert cap["ins"]["client_id"] == "c1"
