"""GET /platform/leads (inbox de plataforma) · gate super_owner. No-super_owner → 403 propagado;
super_owner → lista vía get_platform_leads."""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

mod = importlib.import_module("app.api.routes.platform.router")


def _svc(rows):
    async def get_platform_leads(audience, status, page, limit):
        return rows, len(rows)
    return SimpleNamespace(get_platform_leads=get_platform_leads)


def test_no_super_owner_403(monkeypatch):
    async def _deny(auth):
        raise HTTPException(status_code=403, detail="super_owner_only")
    monkeypatch.setattr(mod, "require_super_owner", _deny)
    with pytest.raises(HTTPException) as e:
        asyncio.run(mod.list_platform_leads(authorization="Bearer x"))
    assert e.value.status_code == 403


def test_super_owner_lista(monkeypatch):
    async def _allow(auth):
        return {"id": "u9"}
    monkeypatch.setattr(mod, "require_super_owner", _allow)
    monkeypatch.setattr(mod, "get_supabase_service", lambda: _svc([{"id": "l1", "audience": "pyme"}]))
    out = asyncio.run(mod.list_platform_leads(authorization="Bearer x"))
    assert out.success is True
    assert out.data["total"] == 1
    assert out.data["leads"][0]["audience"] == "pyme"
