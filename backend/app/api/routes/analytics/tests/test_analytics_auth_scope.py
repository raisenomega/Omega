"""IDOR fix · analytics auth+ownership scope (DEBT-IDOR-ANALYTICS · G9 exime tests).
Molde: aria_v1/tests/test_message_client_scope.py (monkeypatch + asyncio.run).
GET /dashboard/: None→require_superadmin · con client_id→resolve_client_or_403 (variante A).
(Los 6 endpoints legacy de muestra fueron eliminados · Fase C "paridad de verdad"·datos sintéticos.)"""
import asyncio
import importlib
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

# import del MÓDULO router.py (no la instancia APIRouter re-exportada en __init__)
ar = importlib.import_module("app.api.routes.analytics.router")


# ── GET /dashboard/ ──
def test_dashboard_sin_auth_401():
    """Sin Authorization → 401 (get_current_user real lanza antes de tocar DB)."""
    with pytest.raises(HTTPException) as e:
        asyncio.run(ar.get_dashboard(client_id="biz-X", authorization=None))
    assert e.value.status_code == 401


def test_dashboard_client_ajeno_403(monkeypatch):
    """client_id de otro dueño → resolve_client_or_403 lanza 403 (cross-tenant bloqueado)."""
    monkeypatch.setattr(ar, "get_current_user", AsyncMock(return_value={"id": "u1"}))

    def _deny(uid, cid):
        raise HTTPException(status_code=403, detail="client_access_denied")
    monkeypatch.setattr(ar, "resolve_client_or_403", _deny)
    with pytest.raises(HTTPException) as e:
        asyncio.run(ar.get_dashboard(client_id="ajeno", authorization="auth"))
    assert e.value.status_code == 403


def test_dashboard_client_dueno_200(monkeypatch):
    """client_id propio → resolve OK → data filtrada por el client validado."""
    monkeypatch.setattr(ar, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(ar, "resolve_client_or_403", lambda uid, cid: {"id": cid})
    monkeypatch.setattr(ar, "handle_get_dashboard",
                        AsyncMock(return_value={"content_generated": {}, "client_id": "biz-X"}))
    out = asyncio.run(ar.get_dashboard(client_id="biz-X", authorization="auth"))
    assert out.success is True and out.data["client_id"] == "biz-X"


def test_dashboard_none_owner_200(monkeypatch):
    """Sin client_id + role owner → require_superadmin OK → aggregate-all (client_id None)."""
    monkeypatch.setattr(ar, "require_superadmin", AsyncMock(return_value={"id": "owner", "role": "owner"}))
    monkeypatch.setattr(ar, "handle_get_dashboard",
                        AsyncMock(return_value={"content_generated": {}, "client_id": None}))
    out = asyncio.run(ar.get_dashboard(client_id=None, authorization="auth"))
    assert out.success is True


def test_dashboard_none_no_owner_403(monkeypatch):
    """Sin client_id + role != owner → require_superadmin lanza 403 (no ve aggregate-all)."""
    monkeypatch.setattr(ar, "require_superadmin",
                        AsyncMock(side_effect=HTTPException(status_code=403, detail="superadmin_only")))
    with pytest.raises(HTTPException) as e:
        asyncio.run(ar.get_dashboard(client_id=None, authorization="auth"))
    assert e.value.status_code == 403
