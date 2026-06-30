"""REDISEÑO Estrategias Fase C.3 · DELETE /strategies/used-ideas/{usage_id} · ⚠️ BORRADO PERMANENTE.
Espejo del DELETE /strategies/{id} (Fase 2): ownership en el WHERE (.in_('client_id', client_ids) del
SERVIDOR · NUNCA del input) → 404 sin fuga. Routing: la ruta literal used-ideas/{usage_id} va ANTES de
/{strategy_id} (verificado por openapi · trampa starlette 1.x). Test critico: test_delete_idea_ajena_404."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.routes.strategies_v1.handlers import idea_usages as iu
from app.bc_cognition.infrastructure import strategy_idea_usage_repository as usages


def _del(sb):
    return sb.client.table.return_value.delete.return_value.eq.return_value.in_.return_value.execute


def test_delete_idea():
    """Idea del cliente → DELETE real (count 1). WHERE = id exacto + client_id IN client_ids."""
    sb = MagicMock(); _del(sb).return_value.data = [{"id": "u1"}]
    assert usages.delete_idea_usage(sb, "u1", ["biz1"]) == 1
    sb.client.table.return_value.delete.return_value.eq.assert_called_with("id", "u1")
    sb.client.table.return_value.delete.return_value.eq.return_value.in_.assert_called_with("client_id", ["biz1"])


def test_delete_idea_ajena_404():
    """⚠️ CRITICO: idea de OTRO cliente con client_ids=[biz1] → el WHERE client_id IN [biz1] NO la
    matchea → 0 filas → la fila ajena SIGUE EXISTIENDO (nunca se targetea). El guardian vive aqui."""
    sb = MagicMock(); _del(sb).return_value.data = []   # biz2 no esta en [biz1] → DELETE matchea 0 filas
    assert usages.delete_idea_usage(sb, "ajena", ["biz1"]) == 0
    sb.client.table.return_value.delete.return_value.eq.return_value.in_.assert_called_with("client_id", ["biz1"])


def test_delete_idea_sin_client_ids():
    """Sin clientes accesibles → 0 sin tocar supabase (defensivo · no borra nada)."""
    sb = MagicMock()
    assert usages.delete_idea_usage(sb, "u1", []) == 0
    sb.client.table.return_value.delete.assert_not_called()


def _auth(monkeypatch, client_ids):
    monkeypatch.setattr(iu, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(iu.reader, "get_accessible_client_ids", lambda uid: client_ids)
    monkeypatch.setattr(iu, "get_supabase_service", lambda: MagicMock())


def test_delete_handler(monkeypatch):
    """DELETE → 200 {deleted: True, id}. client_ids del servidor (get_accessible_client_ids)."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    monkeypatch.setattr(iu.usages, "delete_idea_usage", lambda sb, uid, cids: cap.update(uid=uid, cids=cids) or 1)
    out = asyncio.run(iu.delete_idea("u1", "auth"))
    assert out == {"deleted": True, "id": "u1"} and cap["uid"] == "u1" and cap["cids"] == ["biz1"]


def test_delete_ownership_handler(monkeypatch):
    """⚠️ idea ajena → repo 0 → 404 sin fuga (NO borra · no revela existencia)."""
    _auth(monkeypatch, ["biz1"]); deleted = []
    monkeypatch.setattr(iu.usages, "delete_idea_usage", lambda *a, **k: deleted.append(1) or 0)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(iu.delete_idea("ajena", "auth"))
    assert ei.value.status_code == 404


def test_delete_idempotente(monkeypatch):
    """Borrar dos veces: la 2a (ya no existe) → repo 0 → 404 (idempotente · no rompe)."""
    _auth(monkeypatch, ["biz1"])
    monkeypatch.setattr(iu.usages, "delete_idea_usage", lambda *a, **k: 0)
    for _ in range(2):
        with pytest.raises(HTTPException) as ei:
            asyncio.run(iu.delete_idea("x", "auth"))
        assert ei.value.status_code == 404


def test_routing_delete_idea_before_strategy():
    """⚠️ la ruta literal used-ideas/{usage_id} se registra ANTES de /{strategy_id} (Fase 2 · openapi)."""
    from fastapi import FastAPI
    from app.api.routes.strategies_v1.router import router
    app = FastAPI(); app.include_router(router)
    paths = list(app.openapi()["paths"].keys())
    assert paths.index("/strategies/used-ideas/{usage_id}") < paths.index("/strategies/{strategy_id}")
