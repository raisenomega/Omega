"""REDISEÑO Estrategias Fase C.2 · archivar IDEA usada (archived_at · migr 00083). list_idea_usages(archived):
Usadas = IS NULL · Archivadas = IS NOT NULL (embed titulo). PATCH /used-ideas/{usage_id}/archive setea
archived_at · scope client_id en el WHERE → 404 sin fuga. Routing: la ruta literal va ANTES de /{strategy_id}. SIN unarchive."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.routes.strategies_v1.handlers import idea_usages as iu
from app.bc_cognition.infrastructure import strategy_idea_usage_repository as usages


def _no_arch(sb):  # cadena del filtro archived_at IS NULL (Usadas)
    return sb.client.table.return_value.select.return_value.in_.return_value.is_.return_value.order.return_value.limit.return_value.execute


def _arch(sb):     # cadena del filtro archived_at IS NOT NULL (Archivadas)
    return sb.client.table.return_value.select.return_value.in_.return_value.not_.is_.return_value.order.return_value.limit.return_value.execute


def test_list_no_archivadas():
    """?archived=false (default) → archived_at IS NULL + embed titulo intacto."""
    sb = MagicMock(); _no_arch(sb).return_value.data = [{"id": "u1", "strategies": {"titulo": "T"}}]
    out = usages.list_idea_usages(sb, ["biz1"], False)
    assert out[0]["strategies"]["titulo"] == "T"
    sb.client.table.return_value.select.return_value.in_.return_value.is_.assert_called_with("archived_at", "null")
    sb.client.table.return_value.select.assert_called_with("*, strategies(titulo)")


def test_list_archivadas():
    """?archived=true → archived_at IS NOT NULL + embed titulo intacto."""
    sb = MagicMock(); _arch(sb).return_value.data = [{"id": "u2", "strategies": {"titulo": "T2"}}]
    out = usages.list_idea_usages(sb, ["biz1"], True)
    assert out[0]["id"] == "u2" and out[0]["strategies"]["titulo"] == "T2"
    sb.client.table.return_value.select.return_value.in_.return_value.not_.is_.assert_called_with("archived_at", "null")


def test_archive_idea():
    """archive_idea_usage → UPDATE archived_at WHERE id + client_id IN client_ids (ownership)."""
    sb = MagicMock()
    sb.client.table.return_value.update.return_value.eq.return_value.in_.return_value.execute.return_value.data = [{"id": "u1"}]
    assert usages.archive_idea_usage(sb, "u1", ["biz1"]) == 1
    assert "archived_at" in sb.client.table.return_value.update.call_args.args[0]
    sb.client.table.return_value.update.return_value.eq.assert_called_with("id", "u1")
    sb.client.table.return_value.update.return_value.eq.return_value.in_.assert_called_with("client_id", ["biz1"])


def test_archive_sin_client_ids():
    """Sin clientes accesibles → 0 sin tocar supabase (defensivo)."""
    sb = MagicMock()
    assert usages.archive_idea_usage(sb, "u1", []) == 0
    sb.client.table.return_value.update.assert_not_called()


def test_archive_idempotente():
    """Archivar 2 veces → no rompe (re-setea archived_at · 1 fila cada vez)."""
    sb = MagicMock()
    sb.client.table.return_value.update.return_value.eq.return_value.in_.return_value.execute.return_value.data = [{"id": "u1"}]
    assert usages.archive_idea_usage(sb, "u1", ["biz1"]) == 1
    assert usages.archive_idea_usage(sb, "u1", ["biz1"]) == 1


def _auth(monkeypatch, client_ids):
    monkeypatch.setattr(iu, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(iu.reader, "get_accessible_client_ids", lambda uid: client_ids)
    monkeypatch.setattr(iu, "get_supabase_service", lambda: MagicMock())


def test_archive_handler(monkeypatch):
    """PATCH archive → 200 {archived: True, id}. client_ids del servidor."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    monkeypatch.setattr(iu.usages, "archive_idea_usage", lambda sb, uid, cids: cap.update(uid=uid, cids=cids) or 1)
    out = asyncio.run(iu.archive_idea("u1", "auth"))
    assert out == {"archived": True, "id": "u1"} and cap["cids"] == ["biz1"]


def test_archive_ownership(monkeypatch):
    """⚠️ idea de OTRO cliente → repo 0 → 404 sin fuga (la idea ajena NO se toca)."""
    _auth(monkeypatch, ["biz1"])
    monkeypatch.setattr(iu.usages, "archive_idea_usage", lambda *a, **k: 0)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(iu.archive_idea("ajena", "auth"))
    assert ei.value.status_code == 404


def test_used_ideas_archived_param(monkeypatch):
    """GET used-ideas pasa el flag archived al list (default false)."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    monkeypatch.setattr(iu.usages, "list_idea_usages", lambda sb, cids, arch: cap.update(arch=arch) or [])
    asyncio.run(iu.used_ideas(True, "auth"))
    assert cap["arch"] is True


def test_routing_archive_before_delete():
    """⚠️ used-ideas/{usage_id}/archive registrada ANTES de /{strategy_id} (Fase 2 · starlette 1.x: openapi)."""
    from fastapi import FastAPI
    from app.api.routes.strategies_v1.router import router
    app = FastAPI(); app.include_router(router)
    paths = list(app.openapi()["paths"].keys())
    assert paths.index("/strategies/used-ideas/{usage_id}/archive") < paths.index("/strategies/{strategy_id}")
