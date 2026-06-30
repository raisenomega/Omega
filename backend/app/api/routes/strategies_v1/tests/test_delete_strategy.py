"""ESTRATEGIAS FASE 2 Commit B · DELETE /strategies/{id} · BORRADO PERMANENTE (hard delete).
Espejo de update_status: el ownership vive en el WHERE (.in_('client_id', client_ids) · client_ids
del SERVIDOR · NUNCA del input) → 404 sin fuga. Test critico: test_delete_ajena_404 (la estrategia
de otro cliente NUNCA entra en el scope del DELETE · sigue existiendo)."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.routes.strategies_v1.handlers import delete_strategy as ds
from app.bc_cognition.infrastructure import strategy_repository as strat


def _del(sb):
    return sb.client.table.return_value.delete.return_value.eq.return_value.in_.return_value.execute


def test_delete_propia():
    """Estrategia del cliente → DELETE real (count 1). WHERE = id exacto + client_id IN client_ids."""
    sb = MagicMock(); _del(sb).return_value.data = [{"id": "s1"}]
    assert strat.delete_strategy(sb, "s1", ["biz1"]) == 1
    sb.client.table.return_value.delete.return_value.eq.assert_called_with("id", "s1")
    sb.client.table.return_value.delete.return_value.eq.return_value.in_.assert_called_with("client_id", ["biz1"])


def test_delete_ajena_404():
    """⚠️ CRITICO: estrategia de OTRO cliente (biz2) con client_ids=[biz1] → el WHERE client_id IN
    [biz1] NO la matchea → 0 filas → la fila ajena SIGUE EXISTIENDO (nunca se targetea). El guardian
    de ownership vive aqui: client_ids del servidor en el WHERE, jamas el input del usuario."""
    sb = MagicMock(); _del(sb).return_value.data = []   # biz2 no esta en [biz1] → DELETE matchea 0 filas
    assert strat.delete_strategy(sb, "ajena", ["biz1"]) == 0
    sb.client.table.return_value.delete.return_value.eq.return_value.in_.assert_called_with("client_id", ["biz1"])


def test_delete_sin_client_ids():
    """Sin clientes accesibles → 0 sin tocar supabase (defensivo · no borra nada · igual que record_use)."""
    sb = MagicMock()
    assert strat.delete_strategy(sb, "s1", []) == 0
    sb.client.table.return_value.delete.assert_not_called()


def test_delete_no_toca_otras():
    """El WHERE filtra por id exacto (.eq('id', target)) → borrar una NO alcanza a otras del cliente."""
    sb = MagicMock(); _del(sb).return_value.data = [{"id": "target"}]
    strat.delete_strategy(sb, "target", ["biz1"])
    sb.client.table.return_value.delete.return_value.eq.assert_called_with("id", "target")


def _auth(monkeypatch, client_ids):
    monkeypatch.setattr(ds, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(ds.reader, "get_accessible_client_ids", lambda uid: client_ids)
    monkeypatch.setattr(ds, "get_supabase_service", lambda: MagicMock())


def test_delete_handler_propia(monkeypatch):
    """Repo borra 1 → 200 {deleted: True, id}. client_ids del servidor (get_accessible_client_ids)."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    def _fake(sb, sid, cids): cap.update(sid=sid, cids=cids); return 1
    monkeypatch.setattr(ds.strat, "delete_strategy", _fake)
    out = asyncio.run(ds.delete_strategy("s1", "auth"))
    assert out == {"deleted": True, "id": "s1"} and cap["sid"] == "s1" and cap["cids"] == ["biz1"]


def test_delete_ajena_404_handler(monkeypatch):
    """Estrategia ajena → repo 0 filas → 404 strategy_not_found (sin revelar que existe · sin fuga)."""
    _auth(monkeypatch, ["biz1"])
    monkeypatch.setattr(ds.strat, "delete_strategy", lambda *a, **k: 0)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(ds.delete_strategy("ajena", "auth"))
    assert ei.value.status_code == 404


def test_delete_inexistente_y_idempotente(monkeypatch):
    """id inexistente → 404. Borrar dos veces: la 2a (ya no existe) → repo 0 → 404 (idempotente · no rompe)."""
    _auth(monkeypatch, ["biz1"])
    monkeypatch.setattr(ds.strat, "delete_strategy", lambda *a, **k: 0)
    for _ in range(2):
        with pytest.raises(HTTPException) as ei:
            asyncio.run(ds.delete_strategy("x", "auth"))
        assert ei.value.status_code == 404
