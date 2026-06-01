"""POST /publish/auto · DEBT-LIMIT1: publica contra el negocio ACTIVO (request.client_id), validado
por resolve_client_or_403 (ownership). G9 exime tests. get_current_user/resolve/publish MOCKEADOS."""
import asyncio

import pytest
from fastapi import HTTPException

import importlib

from app.api.routes.publishing._publish_service import PublishResult
from app.api.routes.publishing.models import AutoPublishRequest

# importlib: el modulo real (el __init__ del paquete bindea 'router'=APIRouter y shadowea el submodulo)
rt = importlib.import_module("app.api.routes.publishing.router")


def test_usa_client_id_del_request_no_limit1(monkeypatch):
    seen = {}
    async def _user(auth): return {"id": "u1"}
    def _resolve(uid, cid): seen["resolve"] = (uid, cid); return {"id": cid}
    async def _publish(pid, cid): seen["publish"] = (pid, cid); return PublishResult(True, "pp1")
    monkeypatch.setattr(rt, "get_current_user", _user)
    monkeypatch.setattr(rt, "resolve_client_or_403", _resolve)
    monkeypatch.setattr(rt, "publish_scheduled_post", _publish)
    out = asyncio.run(rt.auto_publish(AutoPublishRequest(scheduled_post_id="p1", client_id="c_activo"), None))
    assert out.published is True
    assert seen["resolve"] == ("u1", "c_activo")  # valida el negocio ACTIVO (no el primero LIMIT 1)
    assert seen["publish"] == ("p1", "c_activo")   # publica contra el negocio activo


def test_user_no_dueno_del_negocio_403(monkeypatch):
    async def _user(auth): return {"id": "u1"}
    def _resolve(uid, cid): raise HTTPException(status_code=403, detail="client_access_denied")
    monkeypatch.setattr(rt, "get_current_user", _user)
    monkeypatch.setattr(rt, "resolve_client_or_403", _resolve)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(rt.auto_publish(AutoPublishRequest(scheduled_post_id="p1", client_id="ajeno"), None))
    assert ei.value.status_code == 403  # ownership: no se publica en negocio ajeno
