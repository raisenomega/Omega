"""REDISEÑO Estrategias Fase A · POST /{id}/use-idea (registra 1 idea · flip a 'used' SOLO cuando
TODAS) + GET /used-ideas (list scope client). Ownership en el WHERE (client_ids del servidor) → 404
sin fuga. Idempotente: upsert on_conflict(strategy_id,idea_idx) ignore_duplicates (UNIQUE 00082)."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.routes.strategies_v1.handlers import idea_usages as iu
from app.bc_cognition.infrastructure import strategy_idea_usage_repository as usages


def test_record_idea_use_upsert_idempotente():
    """INSERT idempotente: upsert on_conflict (strategy_id,idea_idx) ignore_duplicates (UNIQUE respalda)."""
    sb = MagicMock()
    usages.record_idea_use(sb, "s1", "biz1", 1, "instagram", "idea")
    args, kw = sb.client.table.return_value.upsert.call_args
    assert args[0] == {"strategy_id": "s1", "client_id": "biz1", "idea_idx": 1, "platform": "instagram", "brief": "idea"}
    assert kw["on_conflict"] == "strategy_id,idea_idx" and kw["ignore_duplicates"] is True


def test_count_idea_usages():
    sb = MagicMock()
    sb.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"idea_idx": 0}, {"idea_idx": 1}]
    assert usages.count_idea_usages(sb, "s1") == 2


def test_list_idea_usages_scope():
    """list scope .in_('client_id', client_ids) + filtro archived_at IS NULL (Usadas); sin client_ids → []."""
    sb = MagicMock()
    sb.client.table.return_value.select.return_value.in_.return_value.is_.return_value.order.return_value.limit.return_value.execute.return_value.data = [{"id": "u1"}]
    assert usages.list_idea_usages(sb, ["biz1"])[0]["id"] == "u1"
    sb.client.table.return_value.select.return_value.in_.assert_called_with("client_id", ["biz1"])
    assert usages.list_idea_usages(MagicMock(), []) == []


def _auth(monkeypatch, client_ids):
    monkeypatch.setattr(iu, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(iu.reader, "get_accessible_client_ids", lambda uid: client_ids)
    monkeypatch.setattr(iu, "get_supabase_service", lambda: MagicMock())


def _strat3():  # estrategia del cliente con 3 ideas en posts_sugeridos
    return {"id": "s1", "client_id": "biz1", "contenido": {"posts_sugeridos": [{}, {}, {}]}}


def test_use_idea_inserta(monkeypatch):
    """use-idea → record_idea_use con los datos de la idea (el insert real ocurre)."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    monkeypatch.setattr(iu.strat, "get_strategy_owned", lambda *a: _strat3())
    monkeypatch.setattr(iu.usages, "record_idea_use", lambda sb, sid, cid, idx, p, b: cap.update(sid=sid, cid=cid, idx=idx, p=p, b=b))
    monkeypatch.setattr(iu.usages, "count_idea_usages", lambda *a: 1)
    monkeypatch.setattr(iu.strat, "update_strategy_status", lambda *a: 1)
    out = asyncio.run(iu.use_idea("s1", iu.UseIdeaBody(idea_idx=1, platform="instagram", brief="x"), "auth"))
    assert cap == {"sid": "s1", "cid": "biz1", "idx": 1, "p": "instagram", "b": "x"} and out["all_used"] is False


def test_flip_solo_cuando_todas(monkeypatch):
    """⚠️ flip a 'used' SOLO cuando count==total. 2 de 3 → active (no flip). 3 de 3 → used (flip)."""
    _auth(monkeypatch, ["biz1"]); flips = []
    monkeypatch.setattr(iu.strat, "get_strategy_owned", lambda *a: _strat3())
    monkeypatch.setattr(iu.usages, "record_idea_use", lambda *a: None)
    monkeypatch.setattr(iu.strat, "update_strategy_status", lambda sb, sid, e, cids: flips.append(e))
    monkeypatch.setattr(iu.usages, "count_idea_usages", lambda *a: 2)
    assert asyncio.run(iu.use_idea("s1", iu.UseIdeaBody(idea_idx=1, platform="ig", brief="x"), "a"))["all_used"] is False
    monkeypatch.setattr(iu.usages, "count_idea_usages", lambda *a: 3)
    assert asyncio.run(iu.use_idea("s1", iu.UseIdeaBody(idea_idx=2, platform="ig", brief="y"), "a"))["all_used"] is True
    assert flips == ["used"]   # un solo flip, recien cuando se usaron las 3


def test_use_idea_ownership(monkeypatch):
    """⚠️ estrategia ajena → get_strategy_owned None → 404 + NO inserta (sin fuga)."""
    _auth(monkeypatch, ["biz1"]); inserted = []
    monkeypatch.setattr(iu.strat, "get_strategy_owned", lambda *a: None)
    monkeypatch.setattr(iu.usages, "record_idea_use", lambda *a: inserted.append(1))
    with pytest.raises(HTTPException) as ei:
        asyncio.run(iu.use_idea("ajena", iu.UseIdeaBody(idea_idx=0, platform="ig", brief="x"), "a"))
    assert ei.value.status_code == 404 and inserted == []


def test_list_used_ideas(monkeypatch):
    """GET used-ideas → las ideas usadas del cliente (scope client_ids del servidor)."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    monkeypatch.setattr(iu.usages, "list_idea_usages", lambda sb, cids, arch: cap.update(cids=cids) or [{"id": "u1", "brief": "idea"}])
    out = asyncio.run(iu.used_ideas(False, "auth"))
    assert out["items"][0]["brief"] == "idea" and cap["cids"] == ["biz1"]
